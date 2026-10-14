"""Manages pipelines: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import anomaly_query_service_pb2_grpc as anomalies_v1_anomaly_query_service_pb2_grpc
from acme.careplans.v1 import care_plan_service_pb2 as careplans_v1_care_plan_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.drivers.v1 import driver_query_service_pb2 as drivers_v1_driver_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2 as modelregistry_v1_model_version_validation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_query_service_pb2 as pipelines_v1_pipeline_run_query_service_pb2
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2
from acme.pipelines.v1 import pipeline_service_pb2_grpc as pipelines_v1_pipeline_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineUpdatePipeline1Adapter
from acme_data.domains.pipelines.adapters import PipelineUpdatePipeline1Port
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineServicer(pipelines_v1_pipeline_service_pb2_grpc.PipelineServiceServicer):
    deps: Dependencies

    @rpc_errors
    async def BatchCreatePipelines(
        self, requests: AsyncIterator[
            pipelines_v1_pipeline_service_pb2.BatchCreatePipelinesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_service_pb2.BatchCreatePipelinesResponse:
        """Takes a stream of pipelines and answers once at the end."""
        response = pipelines_v1_pipeline_service_pb2.BatchCreatePipelinesResponse()
        async for request in requests:
            response.MergeFrom(await self.handle_batch_create_pipelines(request))
        return response

    @rpc_errors
    async def ClonePipeline(
        self, request: pipelines_v1_pipeline_service_pb2.ClonePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_service_pb2.ClonePipelineResponse:
        """Creates a pipeline."""
        return await self.handle_clone_pipeline(request)

    @rpc_errors
    async def CreatePipeline(
        self, request: pipelines_v1_pipeline_service_pb2.CreatePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_service_pb2.CreatePipelineResponse:
        """Creates a pipeline."""
        return await self.handle_create_pipeline(request)

    @rpc_errors
    async def DeletePipeline(
        self, request: pipelines_v1_pipeline_service_pb2.DeletePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_service_pb2.DeletePipelineResponse:
        """Deletes a pipeline."""
        return await self.handle_delete_pipeline(request)

    @rpc_errors
    @retry_transient
    async def GetPipeline(
        self, request: pipelines_v1_pipeline_service_pb2.GetPipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_service_pb2.GetPipelineResponse:
        """Returns a pipeline."""
        return await self.handle_get_pipeline(request)

    @rpc_errors
    @retry_transient
    async def ListPipelines(
        self, request: pipelines_v1_pipeline_service_pb2.ListPipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_service_pb2.ListPipelinesResponse:
        """Lists pipelines a page at a time."""
        return await self.handle_list_pipelines(request)

    @rpc_errors
    @retry_transient
    async def SearchPipelines(
        self, request: pipelines_v1_pipeline_service_pb2.SearchPipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_service_pb2.SearchPipelinesResponse:
        """Lists pipelines a page at a time."""
        return await self.handle_search_pipelines(request)

    @rpc_errors
    async def UpdatePipeline(
        self, request: pipelines_v1_pipeline_service_pb2.UpdatePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_service_pb2.UpdatePipelineResponse:
        """Changes a pipeline."""
        return await self.handle_update_pipeline(request)

    async def handle_batch_create_pipelines(
        self,
        request: pipelines_v1_pipeline_service_pb2.BatchCreatePipelinesRequest
    ) -> pipelines_v1_pipeline_service_pb2.BatchCreatePipelinesResponse:
        """Takes a stream of pipelines and answers once at the end."""
        deps = self.deps
        response = pipelines_v1_pipeline_service_pb2.BatchCreatePipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BatchCreatePipelines', extra={'fields': {'sequence': request.sequence}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BatchCreatePipelines',
                {'sequence': request.sequence}
            )
            if request.WhichOneof('chunk') == 'record':
                await deps.repository.save_pipeline(request.context.tenant_id, request.record)
            response_0 = pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsResponse()
            response_1 = drivers_v1_driver_query_service_pb2.FindDriversResponse()
            response_2 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse()
            outgoing_0 = pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsRequest.Filter(
                    created_after=request.record.audit.created_at,
                    owner_id=request.record.pipeline_id,
                    region=request.record.location.region
                )
            )
            outgoing_1 = drivers_v1_driver_query_service_pb2.FindDriversRequest(
                context=request.context,
                filter=drivers_v1_driver_query_service_pb2.FindDriversRequest.Filter(
                    created_after=request.record.audit.updated_at,
                    labels=dict(request.record.metadata),
                    owner_id=request.record.pipeline_id,
                    region=request.record.location.region
                )
            )
            outgoing_2 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        recipient=request.record.location.recipient,
                        region=request.record.location.region
                    )
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.pipelines_pipeline_run_query.BrowsePipelineRuns(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.drivers_driver_query.FindDrivers(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.pipelines_pipeline_step_calculation.ComparePipelineStepOptions(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            return response

    async def handle_clone_pipeline(
        self,
        request: pipelines_v1_pipeline_service_pb2.ClonePipelineRequest
    ) -> pipelines_v1_pipeline_service_pb2.ClonePipelineResponse:
        """Creates a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_service_pb2.ClonePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ClonePipeline', extra={'fields': {'request_id': request.request_id}})
            await deps.repository.audit(request.context.tenant_id, 'ClonePipeline', {'request_id': request.request_id})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_run_query_service_pb2.ExportPipelineRunsResponse()
            response_1 = labeling_v1_annotation_validation_service_pb2.ScoreAnnotationResponse()
            response_2 = metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsResponse()
            outgoing_0 = pipelines_v1_pipeline_run_query_service_pb2.ExportPipelineRunsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_run_query_service_pb2.ExportPipelineRunsRequest.Filter(
                    created_after=request.pipeline.audit.updated_at,
                    region=request.pipeline.location.region
                )
            )
            async for chunk_0 in deps.clients.pipelines_pipeline_run_query.ExportPipelineRuns(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = labeling_v1_annotation_validation_service_pb2.ScoreAnnotationRequest(
                context=request.context,
                details=labeling_v1_annotation_validation_service_pb2.ScoreAnnotationRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(recipient=request.pipeline.location.recipient)
                )
            )
            response_1 = await deps.clients.labeling_annotation_validation.ScoreAnnotation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsRequest.Filter(
                    region=request.pipeline.location.region
                )
            )
            async for chunk_2 in deps.clients.metrics_metric_alert_query.ExportMetricAlerts(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.pipeline.status
            response.pipeline.status = echoed_0
            echoed_1 = request.pipeline.metadata
            response.pipeline.metadata.update(echoed_1)
            return response

    async def handle_create_pipeline(
        self,
        request: pipelines_v1_pipeline_service_pb2.CreatePipelineRequest
    ) -> pipelines_v1_pipeline_service_pb2.CreatePipelineResponse:
        """Creates a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_service_pb2.CreatePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CreatePipeline', extra={'fields': {'request_id': request.request_id}})
            await deps.repository.audit(request.context.tenant_id, 'CreatePipeline', {'request_id': request.request_id})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = careplans_v1_care_plan_service_pb2.CreateCarePlanResponse()
            response_1 = modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionResponse()
            response_2 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse()
            response_3 = pipelines_v1_pipeline_run_query_service_pb2.ExportPipelineRunsResponse()
            fields_0: dict[str, Any] = {
                'care_plan': {
                    'audit': {'created_by': request.pipeline.audit.created_by, 'etag': request.pipeline.audit.etag},
                    'billing_address': {
                        'locality': request.pipeline.location.locality,
                        'region': request.pipeline.location.region
                    }
                },
                'context': request.context
            }
            outgoing_0 = careplans_v1_care_plan_service_pb2.CreateCarePlanRequest(**fields_0)
            response_0 = await deps.clients.careplans_care_plan.CreateCarePlan(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    correlation_id=response_0.result.correlation_id,
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.pipeline.organizer.display_name,
                        email=request.pipeline.organizer.email
                    )
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionRequest()
            )
            response_1 = await deps.clients.modelregistry_model_version_validation.NormalizeModelVersion(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.care_plan.billing_address.country_code
                    )
                ),
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.pipeline.audit.etag,
                        updated_at=response_0.care_plan.audit.updated_at
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_1.model_version.subject.display_name)
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(
                document_2,
                pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest()
            )
            response_2 = await deps.clients.pipelines_pipeline_step_calculation.ComparePipelineStepOptions(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = pipelines_v1_pipeline_run_query_service_pb2.ExportPipelineRunsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_run_query_service_pb2.ExportPipelineRunsRequest.Filter(
                    created_after=response_1.model_version.occurred_at,
                    region=request.pipeline.location.region
                )
            )
            async for chunk_3 in deps.clients.pipelines_pipeline_run_query.ExportPipelineRuns(
                outgoing_3,
                timeout=deps.settings.timeout
            ):
                response_3 = chunk_3
            returned_0_0 = response_0.care_plan.counterparty.display_name
            if returned_0_0:
                response.pipeline.organizer.display_name = returned_0_0
            returned_0_1 = response_0.care_plan.metadata
            response.pipeline.metadata.update(returned_0_1)
            returned_1_0 = response_1.model_version.subject.email
            if returned_1_0:
                response.pipeline.organizer.email = returned_1_0
            returned_2_0 = response_2.pipeline_step.audit.created_by
            if returned_2_0:
                response.pipeline.audit.created_by = returned_2_0
            returned_2_1 = response_2.pipeline_step.audit.created_at
            if returned_2_1.ListFields():
                response.pipeline.audit.created_at.MergeFrom(returned_2_1)
            echoed_0 = request.pipeline.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.status
            response.pipeline.status = echoed_1
            return response

    async def handle_delete_pipeline(
        self,
        request: pipelines_v1_pipeline_service_pb2.DeletePipelineRequest
    ) -> pipelines_v1_pipeline_service_pb2.DeletePipelineResponse:
        """Deletes a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_service_pb2.DeletePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeletePipeline', extra={'fields': {'etag': request.etag}})
            await deps.repository.audit(request.context.tenant_id, 'DeletePipeline', {'etag': request.etag})
            response_0 = metrics_v1_metric_alert_query_service_pb2.ResolveMetricAlertsResponse()
            response_1 = anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesResponse()
            response_2 = pipelines_v1_pipeline_validation_service_pb2.GetPipelineRulesResponse()
            outgoing_0 = metrics_v1_metric_alert_query_service_pb2.ResolveMetricAlertsRequest(context=request.context)
            outgoing_2 = pipelines_v1_pipeline_validation_service_pb2.GetPipelineRulesRequest(
                context=request.context,
                pipeline_id=request.pipeline_id
            )
            response_0, response_2 = await asyncio.gather(
                deps.clients.metrics_metric_alert_query.ResolveMetricAlerts(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.pipelines_pipeline_validation.GetPipelineRules(outgoing_2, timeout=deps.settings.timeout),
            )
            outgoing_1 = anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesRequest.Details(
                    filters=dict(response_0.result.details)
                ),
                reason=request.reason
            )
            registered_1 = cast(
                anomalies_v1_anomaly_query_service_pb2_grpc.AnomalyQueryServiceStub,
                deps.clients.registry['acme.anomalies.v1.AnomalyQueryService']
            )
            response_1 = await registered_1.SummarizeAnomalies(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            return response

    async def handle_get_pipeline(
        self,
        request: pipelines_v1_pipeline_service_pb2.GetPipelineRequest
    ) -> pipelines_v1_pipeline_service_pb2.GetPipelineResponse:
        """Returns a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_service_pb2.GetPipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipeline', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(request.context.tenant_id, 'GetPipeline', {'locale': request.context.locale})
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            return response

    async def handle_list_pipelines(
        self,
        request: pipelines_v1_pipeline_service_pb2.ListPipelinesRequest
    ) -> pipelines_v1_pipeline_service_pb2.ListPipelinesResponse:
        """Lists pipelines a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_service_pb2.ListPipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPipelines', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'ListPipelines', {'order_by': request.order_by})
            response_0 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsResponse()
            outgoing_0 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsRequest(
                context=request.context
            )
            response_0 = await deps.clients.modelregistry_registered_model_query.ResolveRegisteredModels(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.page_info.total_size
            if returned_0_0:
                response.page_info.total_size = returned_0_0
            return response

    async def handle_search_pipelines(
        self,
        request: pipelines_v1_pipeline_service_pb2.SearchPipelinesRequest
    ) -> pipelines_v1_pipeline_service_pb2.SearchPipelinesResponse:
        """Lists pipelines a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_service_pb2.SearchPipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SearchPipelines', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SearchPipelines', {'order_by': request.order_by})
            response_0 = labeling_v1_annotation_validation_service_pb2.LintAnnotationsResponse()
            response_1 = pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesResponse()
            outgoing_0 = labeling_v1_annotation_validation_service_pb2.LintAnnotationsRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    attributes=dict(request.filter.labels),
                    occurred_at=request.filter.created_after
                ),
                context=request.context,
                details=labeling_v1_annotation_validation_service_pb2.LintAnnotationsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.labeling_annotation_validation.LintAnnotations(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesRequest(context=request.context)
            response_1 = await hooks.pipeline_search_pipelines1(
                deps.clients.pipelines_pipeline_query,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            return response

    async def handle_update_pipeline(
        self,
        request: pipelines_v1_pipeline_service_pb2.UpdatePipelineRequest
    ) -> pipelines_v1_pipeline_service_pb2.UpdatePipelineResponse:
        """Changes a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_service_pb2.UpdatePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UpdatePipeline', extra={'fields': {'allow_missing': request.allow_missing}})
            await deps.repository.audit(
                request.context.tenant_id,
                'UpdatePipeline',
                {'allow_missing': request.allow_missing}
            )
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationResponse()
            response_1 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewResponse()
            response_2 = labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksResponse()
            for item_0 in request.pipeline.participants:
                outgoing_0 = pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationRequest(
                    context=request.context,
                    pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                        assignee=identity_v1_refs_pb2.UserRef(email=item_0.contact.email)
                    )
                )
                response_0 = await deps.clients.pipelines_pipeline_run_calculation.ExplainPipelineRunCalculation(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewRequest(
                context=request.context,
                details=featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(country_code=request.pipeline.location.country_code)
                )
            )
            port_1: PipelineUpdatePipeline1Port = PipelineUpdatePipeline1Adapter(
                deps.clients.featurestore_feature_view_calculation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksRequest.Filter(
                    created_after=response_0.pipeline_run.customer.starts_at,
                    owner_id=response_1.feature_view.components.get(
                        'primary',
                        featurestore_v1_featurestore_pb2.FeatureViewComponent()
                    ).component_id,
                    region=response_1.feature_view.address.region
                )
            )
            steps_2 = [
                partial(
                    deps.clients.labeling_labeling_task_query.BrowseLabelingTasks,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.feature_view.address.postal_code
            if returned_1_1:
                response.pipeline.location.postal_code = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            echoed_0 = request.pipeline.organizer
            response.pipeline.organizer.CopyFrom(echoed_0)
            echoed_1 = request.pipeline.metadata
            response.pipeline.metadata.update(echoed_1)
            return response
