"""Checks pipelines against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from typing import cast
import asyncio
import logging

import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.keymanagement.v1 import crypto_key_service_pb2 as keymanagement_v1_crypto_key_service_pb2
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import (
    pipeline_calculation_service_pb2_grpc as pipelines_v1_pipeline_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipeline_validation_service_pb2_grpc as pipelines_v1_pipeline_validation_service_pb2_grpc
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineValidationScorePipeline2Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineValidationNormalizePipeline0Command
from acme_data.domains.pipelines.models import to_pipeline_validation_normalize_pipeline0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineValidationServicer(pipelines_v1_pipeline_validation_service_pb2_grpc.PipelineValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckPipelineEligibility(
        self, request: pipelines_v1_pipeline_validation_service_pb2.CheckPipelineEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_validation_service_pb2.CheckPipelineEligibilityResponse:
        """Checks a pipeline."""
        return await self.handle_check_pipeline_eligibility(request)

    @rpc_errors
    @retry_transient
    async def GetPipelineRules(
        self, request: pipelines_v1_pipeline_validation_service_pb2.GetPipelineRulesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_validation_service_pb2.GetPipelineRulesResponse:
        """Returns a pipeline."""
        return await self.handle_get_pipeline_rules(request)

    @rpc_errors
    async def NormalizePipeline(
        self, request: pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineResponse:
        """Normalizes a pipeline."""
        return await self.handle_normalize_pipeline(request)

    @rpc_errors
    async def PreviewPipeline(
        self, request: pipelines_v1_pipeline_validation_service_pb2.PreviewPipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_validation_service_pb2.PreviewPipelineResponse:
        """Previews a pipeline."""
        return await self.handle_preview_pipeline(request)

    @rpc_errors
    async def ScorePipeline(
        self, request: pipelines_v1_pipeline_validation_service_pb2.ScorePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_validation_service_pb2.ScorePipelineResponse:
        """Scores a pipeline."""
        return await self.handle_score_pipeline(request)

    @rpc_errors
    async def ValidatePipeline(
        self, request: pipelines_v1_pipeline_validation_service_pb2.ValidatePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_validation_service_pb2.ValidatePipelineResponse:
        """Validates a pipeline."""
        return await self.handle_validate_pipeline(request)

    async def handle_check_pipeline_eligibility(
        self,
        request: pipelines_v1_pipeline_validation_service_pb2.CheckPipelineEligibilityRequest
    ) -> pipelines_v1_pipeline_validation_service_pb2.CheckPipelineEligibilityResponse:
        """Checks a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_validation_service_pb2.CheckPipelineEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckPipelineEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckPipelineEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineResponse()
            response_1 = keymanagement_v1_crypto_key_service_pb2.WatchCryptoKeysResponse()
            response_2 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsResponse()
            outgoing_0 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.pipeline.participants.add()
            field_0_1_part_1.contact.preferred_channel = request.details.contact.preferred_channel
            outgoing_0.pipeline.weekly.interval = request.pipeline.daily.interval
            merged_0 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.pipelines_pipeline_calculation.CalculatePipeline(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            for item_1 in request.pipeline.participants:
                outgoing_1 = keymanagement_v1_crypto_key_service_pb2.WatchCryptoKeysRequest(
                    context=request.context,
                    subscriber=common_v1_contact_pb2.ContactInfo(
                        name=item_1.contact.name,
                        preferred_channel=item_1.contact.preferred_channel
                    )
                )
                async for result_1 in deps.clients.keymanagement_crypto_key.WatchCryptoKeys(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ):
                    response_1 = result_1
            outgoing_2 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=request.details.contact.email,
                                name=request.details.contact.name
                            )
                        )
                    ]
                )
            )
            registered_2 = cast(
                pipelines_v1_pipeline_calculation_service_pb2_grpc.PipelineCalculationServiceStub,
                deps.clients.registry['acme.pipelines.v1.PipelineCalculationService']
            )
            response_2 = await registered_2.ComparePipelineOptions(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.pipeline.audit.etag
            if returned_0_0:
                response.pipeline.audit.etag = returned_0_0
            returned_2_0 = response_2.pipeline.location.country_code
            if returned_2_0:
                response.pipeline.location.country_code = returned_2_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.metadata
            response.pipeline.metadata.update(echoed_1)
            return response

    async def handle_get_pipeline_rules(
        self,
        request: pipelines_v1_pipeline_validation_service_pb2.GetPipelineRulesRequest
    ) -> pipelines_v1_pipeline_validation_service_pb2.GetPipelineRulesResponse:
        """Returns a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_validation_service_pb2.GetPipelineRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipelineRules', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetPipelineRules',
                {'locale': request.context.locale}
            )
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            return response

    async def handle_normalize_pipeline(
        self,
        request: pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineRequest
    ) -> pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineResponse:
        """Normalizes a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizePipeline', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizePipeline', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunResponse()
            command_0 = PipelineValidationNormalizePipeline0Command(
                context=request.context,
                pipeline_run_assignee_email=request.details.contact.email
            )
            outgoing_0 = to_pipeline_validation_normalize_pipeline0_command(command_0)
            response_0 = await deps.clients.pipelines_pipeline_run_calculation.EstimatePipelineRun(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline_run.audit.updated_at
            if returned_0_0.ListFields():
                response.pipeline.audit.updated_at.MergeFrom(returned_0_0)
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.location
            response.pipeline.location.CopyFrom(echoed_1)
            return response

    async def handle_preview_pipeline(
        self,
        request: pipelines_v1_pipeline_validation_service_pb2.PreviewPipelineRequest
    ) -> pipelines_v1_pipeline_validation_service_pb2.PreviewPipelineResponse:
        """Previews a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_validation_service_pb2.PreviewPipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewPipeline', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewPipeline', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineResponse()
            response_1 = pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineResponse()
            response_2 = labeling_v1_labeling_task_service_pb2.ListLabelingTasksResponse()
            response_3 = pipelines_v1_pipeline_calculation_service_pb2.GetPipelineRatesResponse()
            async for item_0 in async_messages(request.pipeline.participants):
                outgoing_0 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest(
                    context=request.context,
                    pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                        participants=[
                            pipelines_v1_pipelines_pb2.PipelineParticipant(
                                contact=common_v1_contact_pb2.ContactInfo(
                                    email=item_0.contact.email,
                                    phone=item_0.contact.phone,
                                    preferred_channel=item_0.contact.preferred_channel
                                )
                            )
                        ]
                    )
                )
                response_0 = await deps.clients.pipelines_pipeline_calculation.CalculatePipeline(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            for item_1 in request.pipeline.participants:
                outgoing_1 = pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineRequest(
                    context=request.context,
                    pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                        organizer=identity_v1_refs_pb2.UserRef(email=item_1.contact.email)
                    )
                )
                response_1 = await deps.clients.pipelines_pipeline_calculation.SimulatePipeline(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = labeling_v1_labeling_task_service_pb2.ListLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_service_pb2.ListLabelingTasksRequest.Filter(
                    created_after=response_0.pipeline.audit.updated_at,
                    region=response_0.pipeline.location.region
                )
            )
            response_2 = await hooks.pipeline_validation_preview_pipeline2(
                deps.clients.labeling_labeling_task,
                outgoing_2,
                deps.settings.timeout
            )
            outgoing_3 = pipelines_v1_pipeline_calculation_service_pb2.GetPipelineRatesRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.pipeline_id = request.pipeline.pipeline_id
            outgoing_3.context.tenant_id = tenant_id.get()
            response_3 = await deps.clients.pipelines_pipeline_calculation.GetPipelineRates(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_3_0 = response_3.pipeline.audit.updated_by
            if returned_3_0:
                response.pipeline.audit.updated_by = returned_3_0
            returned_3_1 = response_3.pipeline.location.region
            if returned_3_1:
                response.pipeline.location.region = returned_3_1
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.metadata
            response.pipeline.metadata.update(echoed_1)
            return response

    async def handle_score_pipeline(
        self,
        request: pipelines_v1_pipeline_validation_service_pb2.ScorePipelineRequest
    ) -> pipelines_v1_pipeline_validation_service_pb2.ScorePipelineResponse:
        """Scores a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScorePipeline', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScorePipeline', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationResponse()
            response_1 = labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksResponse()
            response_2 = pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineResponse()
            outgoing_0 = pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.pipeline.audit.etag),
                    location=common_v1_address_pb2.PostalAddress(lines=list(request.details.destination.lines)),
                    organizer=identity_v1_refs_pb2.UserRef(user_id=request.pipeline.organizer.user_id),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.pipeline.organizer.email)
                        )
                    ]
                )
            )
            outgoing_1 = labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksRequest(context=request.context)
            response_0, response_1 = await asyncio.gather(
                deps.clients.pipelines_pipeline_calculation.ExplainPipelineCalculation(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.labeling_labeling_task.BatchGetLabelingTasks(outgoing_1, timeout=deps.settings.timeout),
            )
            outgoing_2 = pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineRequest(
                context=request.context,
                details=pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(recipient=response_0.pipeline.location.recipient)
                ),
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    daily=pipelines_v1_pipelines_pb2.PipelineDailyRule(interval=response_0.pipeline.weekly.interval)
                )
            )
            response_2 = await PipelineValidationScorePipeline2Adapter(
                deps.clients.pipelines_pipeline_calculation,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.pipeline.location.country_code
            if returned_0_0:
                response.pipeline.location.country_code = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.metadata
            response.pipeline.metadata.update(echoed_1)
            return response

    async def handle_validate_pipeline(
        self,
        request: pipelines_v1_pipeline_validation_service_pb2.ValidatePipelineRequest
    ) -> pipelines_v1_pipeline_validation_service_pb2.ValidatePipelineResponse:
        """Validates a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_validation_service_pb2.ValidatePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidatePipeline', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidatePipeline', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = ledger_v1_ledger_account_query_service_pb2.ExportLedgerAccountsResponse()
            response_1 = metrics_v1_metric_series_validation_service_pb2.ScoreMetricSeriesResponse()
            outgoing_0 = ledger_v1_ledger_account_query_service_pb2.ExportLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_query_service_pb2.ExportLedgerAccountsRequest.Filter(
                    created_after=request.pipeline.audit.updated_at,
                    region=request.pipeline.location.region
                )
            )
            async for chunk_0 in deps.clients.ledger_ledger_account_query.ExportLedgerAccounts(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = metrics_v1_metric_series_validation_service_pb2.ScoreMetricSeriesRequest(
                context=request.context,
                details=metrics_v1_metric_series_validation_service_pb2.ScoreMetricSeriesRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(recipient=request.pipeline.location.recipient)
                ),
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.pipeline.audit.created_at)
                )
            )
            response_1 = await deps.clients.metrics_metric_series_validation.ScoreMetricSeries(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.metric_series.audit.updated_by
            if returned_1_1:
                response.pipeline.audit.updated_by = returned_1_1
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.organizer
            response.pipeline.organizer.CopyFrom(echoed_1)
            return response
