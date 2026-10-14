"""Builds and schedules reports about annotations."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.appointments.v1 import refs_pb2 as appointments_v1_refs_pb2
from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.careplans.v1 import care_plan_calculation_service_pb2 as careplans_v1_care_plan_calculation_service_pb2
from acme.careplans.v1 import careplans_pb2 as careplans_v1_careplans_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_query_service_pb2 as labeling_v1_annotation_query_service_pb2
from acme.labeling.v1 import annotation_reporting_service_pb2 as labeling_v1_annotation_reporting_service_pb2
from acme.labeling.v1 import annotation_reporting_service_pb2_grpc as labeling_v1_annotation_reporting_service_pb2_grpc
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.modelregistry.v1 import deployment_reporting_service_pb2 as modelregistry_v1_deployment_reporting_service_pb2

from acme_data.domains.labeling.adapters import AnnotationReportingGenerateAnnotationReport1Adapter
from acme_data.domains.labeling.adapters import AnnotationReportingGenerateAnnotationReport1Port
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import AnnotationReportingDeleteAnnotationReport0Command
from acme_data.domains.labeling.models import AnnotationReportingDeleteAnnotationReport1Command
from acme_data.domains.labeling.models import to_annotation_reporting_delete_annotation_report0_command
from acme_data.domains.labeling.models import to_annotation_reporting_delete_annotation_report1_command
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class AnnotationReportingServicer(labeling_v1_annotation_reporting_service_pb2_grpc.AnnotationReportingServiceServicer):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def CountAnnotationTotals(
        self, request: labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsResponse:
        """Counts annotations by status."""
        return await self.handle_count_annotation_totals(request)

    @rpc_errors
    async def DeleteAnnotationReport(
        self, request: labeling_v1_annotation_reporting_service_pb2.DeleteAnnotationReportRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_reporting_service_pb2.DeleteAnnotationReportResponse:
        """Deletes an annotation."""
        return await self.handle_delete_annotation_report(request)

    @rpc_errors
    @retry_transient
    async def FetchAnnotationReport(
        self, request: labeling_v1_annotation_reporting_service_pb2.FetchAnnotationReportRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_reporting_service_pb2.FetchAnnotationReportResponse:
        """Returns an annotation."""
        return await self.handle_fetch_annotation_report(request)

    @rpc_errors
    async def GenerateAnnotationReport(
        self, request: labeling_v1_annotation_reporting_service_pb2.GenerateAnnotationReportRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_reporting_service_pb2.GenerateAnnotationReportResponse:
        """Generates an annotation."""
        return await self.handle_generate_annotation_report(request)

    @rpc_errors
    @retry_transient
    async def ListAnnotationReports(
        self, request: labeling_v1_annotation_reporting_service_pb2.ListAnnotationReportsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_reporting_service_pb2.ListAnnotationReportsResponse:
        """Lists annotations a page at a time."""
        return await self.handle_list_annotation_reports(request)

    @rpc_errors
    async def ShareAnnotationReport(
        self, request: labeling_v1_annotation_reporting_service_pb2.ShareAnnotationReportRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_reporting_service_pb2.ShareAnnotationReportResponse:
        """Shares an annotation."""
        return await self.handle_share_annotation_report(request)

    @stream_errors
    async def StreamAnnotationMetrics(
        self, request: labeling_v1_annotation_reporting_service_pb2.StreamAnnotationMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[labeling_v1_annotation_reporting_service_pb2.StreamAnnotationMetricsResponse]:
        """Streams the changes of annotations as they happen."""
        response = await self.handle_stream_annotation_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_annotation_totals(
        self,
        request: labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsRequest
    ) -> labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsResponse:
        """Counts annotations by status."""
        deps = self.deps
        response = labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountAnnotationTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountAnnotationTotals',
                {'order_by': request.order_by}
            )
            response_0 = labeling_v1_label_set_validation_service_pb2.LintLabelSetsResponse()
            outgoing_0 = labeling_v1_label_set_validation_service_pb2.LintLabelSetsRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    location=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.labeling_label_set_validation.LintLabelSets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            return response

    async def handle_delete_annotation_report(
        self,
        request: labeling_v1_annotation_reporting_service_pb2.DeleteAnnotationReportRequest
    ) -> labeling_v1_annotation_reporting_service_pb2.DeleteAnnotationReportResponse:
        """Deletes an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_reporting_service_pb2.DeleteAnnotationReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteAnnotationReport', extra={'fields': {'annotation_id': request.annotation_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DeleteAnnotationReport',
                {'annotation_id': request.annotation_id}
            )
            response_0 = labeling_v1_label_set_sync_service_pb2.PullLabelSetsResponse()
            response_1 = authorization_v1_access_policy_query_service_pb2.SummarizeAccessPoliciesResponse()
            response_2 = labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityResponse()
            command_0 = AnnotationReportingDeleteAnnotationReport0Command(
                context=request.context,
                label_set_audit_etag=request.etag,
                label_set_children_children_manager_user_id=request.context.actor.user_id,
                label_set_manager_email=request.context.actor.email,
                reason=request.reason
            )
            outgoing_0 = to_annotation_reporting_delete_annotation_report0_command(command_0)
            response_0 = await deps.clients.labeling_label_set_sync.PullLabelSets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = AnnotationReportingDeleteAnnotationReport1Command.model_validate(
                {
                    'context': request.context,
                    'reason': request.reason,
                    'annotations': dict(response_0.result.details),
                    'details_filters': dict(response_0.label_set.attributes)
                }
            )
            outgoing_1 = to_annotation_reporting_delete_annotation_report1_command(command_1)
            response_1 = await deps.clients.authorization_access_policy_query.SummarizeAccessPolicies(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=response_0.label_set.manager.user_id),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.label_set.audit.created_at)
                )
            )
            send_2 = partial(
                deps.clients.labeling_labeling_task_validation.CheckLabelingTaskEligibility,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            return response

    async def handle_fetch_annotation_report(
        self,
        request: labeling_v1_annotation_reporting_service_pb2.FetchAnnotationReportRequest
    ) -> labeling_v1_annotation_reporting_service_pb2.FetchAnnotationReportResponse:
        """Returns an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_reporting_service_pb2.FetchAnnotationReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchAnnotationReport', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'FetchAnnotationReport', {})
            response_0 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskResponse()
            outgoing_0 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.labeling_labeling_task_calculation.QuoteLabelingTask(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.annotation.correlation_id = returned_0_0
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            return response

    async def handle_generate_annotation_report(
        self,
        request: labeling_v1_annotation_reporting_service_pb2.GenerateAnnotationReportRequest
    ) -> labeling_v1_annotation_reporting_service_pb2.GenerateAnnotationReportResponse:
        """Generates an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_reporting_service_pb2.GenerateAnnotationReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateAnnotationReport', extra={'fields': {'annotation_id': request.annotation_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateAnnotationReport',
                {'annotation_id': request.annotation_id}
            )
            response_0 = labeling_v1_label_set_sync_service_pb2.PullLabelSetsResponse()
            response_1 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse()
            response_2 = careplans_v1_care_plan_calculation_service_pb2.SimulateCarePlanResponse()
            outgoing_0 = labeling_v1_label_set_sync_service_pb2.PullLabelSetsRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.label_set.children.add()
            field_0_1_part_2 = field_0_1_part_1.children.add()
            field_0_1_part_2.manager.email = request.context.actor.email
            field_0_2_part_1 = outgoing_0.label_set.children.add()
            field_0_2_part_2 = field_0_2_part_1.children.add()
            field_0_2_part_2.manager.user_id = request.context.actor.user_id
            outgoing_0.reason = request.reason
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.labeling_label_set_sync.PullLabelSets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest(
                context=request.context,
                details=labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(recipient=response_0.label_set.location.recipient)
                ),
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    comments=[
                        labeling_v1_labeling_pb2.LabelingTaskComment(created_at=response_0.label_set.audit.created_at)
                    ]
                )
            )
            port_1: AnnotationReportingGenerateAnnotationReport1Port = AnnotationReportingGenerateAnnotationReport1Adapter(
                deps.clients.labeling_labeling_task_calculation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = careplans_v1_care_plan_calculation_service_pb2.SimulateCarePlanRequest(
                care_plan=careplans_v1_careplans_pb2.CarePlan(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        locality=response_0.label_set.location.locality
                    ),
                    counterparty=appointments_v1_refs_pb2.AppointmentRef(
                        display_name=response_1.labeling_task.customer.display_name
                    ),
                    lines=[careplans_v1_careplans_pb2.CarePlanLine(attributes=dict(response_0.label_set.attributes))]
                ),
                context=request.context,
                details=careplans_v1_care_plan_calculation_service_pb2.SimulateCarePlanRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=response_0.label_set.location.region)
                )
            )
            steps_2 = [
                partial(
                    deps.clients.careplans_care_plan_calculation.SimulateCarePlan,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_annotation_reports(
        self,
        request: labeling_v1_annotation_reporting_service_pb2.ListAnnotationReportsRequest
    ) -> labeling_v1_annotation_reporting_service_pb2.ListAnnotationReportsResponse:
        """Lists annotations a page at a time."""
        deps = self.deps
        response = labeling_v1_annotation_reporting_service_pb2.ListAnnotationReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListAnnotationReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListAnnotationReports',
                {'order_by': request.order_by}
            )
            response_0 = lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowResponse()
            response_1 = labeling_v1_labeling_task_service_pb2.SearchLabelingTasksResponse()
            outgoing_0 = lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    ),
                    comments=[lineage_v1_lineage_pb2.ImpactComment(created_at=request.filter.created_after)]
                )
            )
            response_0 = await deps.clients.lineage_impact_workflow.RetryImpactWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_labeling_task_service_pb2.SearchLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_service_pb2.SearchLabelingTasksRequest.Filter(
                    owner_id=request.filter.owner_id
                )
            )
            response_1 = cast(labeling_v1_labeling_task_service_pb2.SearchLabelingTasksResponse, await deps.bus.request(
                'acme.labeling.v1.AnnotationReportingService/ListAnnotationReports/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            return response

    async def handle_share_annotation_report(
        self,
        request: labeling_v1_annotation_reporting_service_pb2.ShareAnnotationReportRequest
    ) -> labeling_v1_annotation_reporting_service_pb2.ShareAnnotationReportResponse:
        """Shares an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_reporting_service_pb2.ShareAnnotationReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareAnnotationReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ShareAnnotationReport', {'reason': request.reason})
            response_0 = labeling_v1_annotation_query_service_pb2.BrowseAnnotationsResponse()
            response_1 = lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowResponse()
            outgoing_0 = labeling_v1_annotation_query_service_pb2.BrowseAnnotationsRequest(
                context=request.context,
                filter=labeling_v1_annotation_query_service_pb2.BrowseAnnotationsRequest.Filter(
                    owner_id=request.details.template_id
                )
            )
            response_0 = await deps.clients.labeling_annotation_query.BrowseAnnotations(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    requester=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.recipient.preferred_channel
                    )
                )
            )
            method_name_1 = 'RetryImpactWorkflow'
            response_1 = await getattr(
                deps.clients.lineage_impact_workflow,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            return response

    async def handle_stream_annotation_metrics(
        self,
        request: labeling_v1_annotation_reporting_service_pb2.StreamAnnotationMetricsRequest
    ) -> labeling_v1_annotation_reporting_service_pb2.StreamAnnotationMetricsResponse:
        """Streams the changes of annotations as they happen."""
        deps = self.deps
        response = labeling_v1_annotation_reporting_service_pb2.StreamAnnotationMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamAnnotationMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamAnnotationMetrics',
                {'max_events': request.max_events}
            )
            response_0 = labeling_v1_label_set_calculation_service_pb2.CompareLabelSetOptionsResponse()
            response_1 = modelregistry_v1_deployment_reporting_service_pb2.ScheduleDeploymentReportResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'label_set': {
                    'children': [
                        {
                            'children': [
                                {
                                    'location': {'region': request.filter.region},
                                    'manager': {
                                        'email': request.subscriber.email,
                                        'user_id': request.context.actor.user_id
                                    }
                                }
                            ],
                            'manager': {'email': request.context.actor.email}
                        }
                    ]
                }
            }
            outgoing_0 = labeling_v1_label_set_calculation_service_pb2.CompareLabelSetOptionsRequest(**fields_0)
            response_0 = await deps.clients.labeling_label_set_calculation.CompareLabelSetOptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_deployment_reporting_service_pb2.ScheduleDeploymentReportRequest(
                annotations=dict(response_0.result.details),
                context=request.context,
                details=modelregistry_v1_deployment_reporting_service_pb2.ScheduleDeploymentReportRequest.Details(
                    filters=dict(request.filter.labels)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                modelregistry_v1_deployment_reporting_service_pb2.ScheduleDeploymentReportRequest()
            )
            response_1 = await deps.clients.modelregistry_deployment_reporting.ScheduleDeploymentReport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            return response
