"""Moves a label set between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import label_set_lifecycle_service_pb2 as labeling_v1_label_set_lifecycle_service_pb2
from acme.labeling.v1 import label_set_lifecycle_service_pb2_grpc as labeling_v1_label_set_lifecycle_service_pb2_grpc
from acme.labeling.v1 import label_set_reporting_service_pb2 as labeling_v1_label_set_reporting_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.lineage.v1 import impact_reporting_service_pb2 as lineage_v1_impact_reporting_service_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.timekeeping.v1 import timesheet_service_pb2 as timekeeping_v1_timesheet_service_pb2
from acme.yards.v1 import yard_service_pb2 as yards_v1_yard_service_pb2

from acme_data.domains.labeling import hooks
from acme_data.domains.labeling.adapters import LabelSetLifecycleActivateLabelSet0Adapter
from acme_data.domains.labeling.adapters import LabelSetLifecycleTerminateLabelSet0Adapter
from acme_data.domains.labeling.adapters import LabelSetLifecycleTerminateLabelSet0Port
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import LabelSetLifecycleRenewLabelSet0Command
from acme_data.domains.labeling.models import LabelSetLifecycleScheduleLabelSetExpiry0Command
from acme_data.domains.labeling.models import to_label_set_lifecycle_renew_label_set0_command
from acme_data.domains.labeling.models import to_label_set_lifecycle_schedule_label_set_expiry0_command
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class LabelSetLifecycleServicer(labeling_v1_label_set_lifecycle_service_pb2_grpc.LabelSetLifecycleServiceServicer):
    deps: Dependencies

    @rpc_errors
    async def ActivateLabelSet(
        self, request: labeling_v1_label_set_lifecycle_service_pb2.ActivateLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_lifecycle_service_pb2.ActivateLabelSetResponse:
        """Activates a label set."""
        return await self.handle_activate_label_set(request)

    @rpc_errors
    async def ExpireLabelSet(
        self, request: labeling_v1_label_set_lifecycle_service_pb2.ExpireLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_lifecycle_service_pb2.ExpireLabelSetResponse:
        """Expires a label set."""
        return await self.handle_expire_label_set(request)

    @rpc_errors
    @retry_transient
    async def GetLabelSetLifecycle(
        self, request: labeling_v1_label_set_lifecycle_service_pb2.GetLabelSetLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_lifecycle_service_pb2.GetLabelSetLifecycleResponse:
        """Returns a label set."""
        return await self.handle_get_label_set_lifecycle(request)

    @rpc_errors
    async def ReinstateLabelSet(
        self, request: labeling_v1_label_set_lifecycle_service_pb2.ReinstateLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_lifecycle_service_pb2.ReinstateLabelSetResponse:
        """Reinstates a label set."""
        return await self.handle_reinstate_label_set(request)

    @rpc_errors
    async def RenewLabelSet(
        self, request: labeling_v1_label_set_lifecycle_service_pb2.RenewLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_lifecycle_service_pb2.RenewLabelSetResponse:
        """Renews a label set."""
        return await self.handle_renew_label_set(request)

    @rpc_errors
    async def ScheduleLabelSetExpiry(
        self, request: labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryResponse:
        """Schedules a label set."""
        return await self.handle_schedule_label_set_expiry(request)

    @rpc_errors
    async def SuspendLabelSet(
        self, request: labeling_v1_label_set_lifecycle_service_pb2.SuspendLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_lifecycle_service_pb2.SuspendLabelSetResponse:
        """Suspends a label set."""
        return await self.handle_suspend_label_set(request)

    @rpc_errors
    async def TerminateLabelSet(
        self, request: labeling_v1_label_set_lifecycle_service_pb2.TerminateLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_lifecycle_service_pb2.TerminateLabelSetResponse:
        """Terminates a label set."""
        return await self.handle_terminate_label_set(request)

    async def handle_activate_label_set(
        self,
        request: labeling_v1_label_set_lifecycle_service_pb2.ActivateLabelSetRequest
    ) -> labeling_v1_label_set_lifecycle_service_pb2.ActivateLabelSetResponse:
        """Activates a label set."""
        deps = self.deps
        response = labeling_v1_label_set_lifecycle_service_pb2.ActivateLabelSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateLabelSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivateLabelSet', {'reason': request.reason})
            response_0 = lineage_v1_impact_reporting_service_pb2.ShareImpactReportResponse()
            response_1 = authorization_v1_access_policy_service_pb2.BatchGetAccessPoliciesResponse()
            outgoing_0 = lineage_v1_impact_reporting_service_pb2.ShareImpactReportRequest(
                context=request.context,
                details=lineage_v1_impact_reporting_service_pb2.ShareImpactReportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        name=request.details.notify_contact.name,
                        phone=request.details.notify_contact.phone,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                )
            )
            response_0 = await LabelSetLifecycleActivateLabelSet0Adapter(
                deps.clients.lineage_impact_reporting,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = authorization_v1_access_policy_service_pb2.BatchGetAccessPoliciesRequest(
                context=request.context
            )
            response_1 = cast(authorization_v1_access_policy_service_pb2.BatchGetAccessPoliciesResponse, await deps.bus.request(
                'acme.labeling.v1.LabelSetLifecycleService/ActivateLabelSet/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.impact.requester.email
            returned_0_0_part_1 = response.label_set.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            if returned_0_0:
                returned_0_0_part_2.manager.email = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_label_set(
        self,
        request: labeling_v1_label_set_lifecycle_service_pb2.ExpireLabelSetRequest
    ) -> labeling_v1_label_set_lifecycle_service_pb2.ExpireLabelSetResponse:
        """Expires a label set."""
        deps = self.deps
        response = labeling_v1_label_set_lifecycle_service_pb2.ExpireLabelSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireLabelSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireLabelSet', {'reason': request.reason})
            response_0 = labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksResponse()
            response_1 = metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesResponse()
            response_2 = anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowResponse()
            response_3 = yards_v1_yard_service_pb2.BatchGetYardsResponse()
            outgoing_0 = labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.annotations),
                    owner_id=request.details.new_owner.user_id
                )
            )
            response_0 = await deps.clients.labeling_labeling_task_query.FindLabelingTasks(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesRequest(
                context=request.context,
                details=metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.details.new_owner.email)
                )
            )
            method_name_1 = 'SubscribeMetricSeriesUpdates'
            response_1 = await getattr(
                deps.clients.metrics_metric_series_notification,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {
                'anomaly': {
                    'assignee': {
                        'email': request.details.new_owner.email,
                        'user_id': response_1.metric_series.owner.user_id
                    }
                },
                'context': request.context,
                'details': {
                    'notify': {
                        'phone': request.details.notify_contact.phone,
                        'preferred_channel': request.details.notify_contact.preferred_channel
                    }
                }
            }
            outgoing_2 = anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowRequest(**fields_2)
            response_2 = await deps.clients.anomalies_anomaly_workflow.StartAnomalyWorkflow(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = yards_v1_yard_service_pb2.BatchGetYardsRequest(context=request.context)
            document_3 = MessageToDict(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = ParseDict(document_3, yards_v1_yard_service_pb2.BatchGetYardsRequest())
            response_3 = await deps.clients.yards_yard.BatchGetYards(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.metric_series.name
            returned_1_0_part_1 = response.label_set.children.add()
            if returned_1_0:
                returned_1_0_part_1.name = returned_1_0
            returned_1_1 = response_1.metric_series.owner.email
            returned_1_1_part_1 = response.label_set.children.add()
            if returned_1_1:
                returned_1_1_part_1.manager.email = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_label_set_lifecycle(
        self,
        request: labeling_v1_label_set_lifecycle_service_pb2.GetLabelSetLifecycleRequest
    ) -> labeling_v1_label_set_lifecycle_service_pb2.GetLabelSetLifecycleResponse:
        """Returns a label set."""
        deps = self.deps
        response = labeling_v1_label_set_lifecycle_service_pb2.GetLabelSetLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLabelSetLifecycle', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLabelSetLifecycle', {})
            response_0 = metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesResponse()
            response_1 = labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsResponse()
            outgoing_0 = metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.metrics_dashboard_notification.UnsubscribeDashboardUpdates(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.region = response_0.dashboard.billing_address.region
            merged_1 = labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.labeling_label_set_sync.ListLabelSetConflicts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.billing_address.postal_code
            if returned_0_0:
                response.label_set.location.postal_code = returned_0_0
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            return response

    async def handle_reinstate_label_set(
        self,
        request: labeling_v1_label_set_lifecycle_service_pb2.ReinstateLabelSetRequest
    ) -> labeling_v1_label_set_lifecycle_service_pb2.ReinstateLabelSetResponse:
        """Reinstates a label set."""
        deps = self.deps
        response = labeling_v1_label_set_lifecycle_service_pb2.ReinstateLabelSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstateLabelSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReinstateLabelSet', {'reason': request.reason})
            response_0 = timekeeping_v1_timesheet_service_pb2.BatchGetTimesheetsResponse()
            response_1 = labeling_v1_label_set_validation_service_pb2.ScoreLabelSetResponse()
            outgoing_0 = timekeeping_v1_timesheet_service_pb2.BatchGetTimesheetsRequest(context=request.context)
            outgoing_1 = labeling_v1_label_set_validation_service_pb2.ScoreLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.new_owner.email)
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(display_name=request.details.new_owner.display_name)
                        )
                    ],
                    manager=identity_v1_refs_pb2.UserRef(email=request.details.notify_contact.email)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.timekeeping_timesheet.BatchGetTimesheets(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.labeling_label_set_validation.ScoreLabelSet(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.label_set.depth
            returned_1_0_part_1 = response.label_set.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            returned_1_0_part_3 = returned_1_0_part_2.children.add()
            if returned_1_0:
                returned_1_0_part_3.depth = returned_1_0
            returned_1_1 = response_1.label_set.location.postal_code
            returned_1_1_part_1 = response.label_set.children.add()
            if returned_1_1:
                returned_1_1_part_1.location.postal_code = returned_1_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_renew_label_set(
        self,
        request: labeling_v1_label_set_lifecycle_service_pb2.RenewLabelSetRequest
    ) -> labeling_v1_label_set_lifecycle_service_pb2.RenewLabelSetResponse:
        """Renews a label set."""
        deps = self.deps
        response = labeling_v1_label_set_lifecycle_service_pb2.RenewLabelSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewLabelSet', extra={'fields': {'reason_code': request.details.reason_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RenewLabelSet',
                {'reason_code': request.details.reason_code}
            )
            response_0 = authorization_v1_access_policy_service_pb2.UpdateAccessPolicyResponse()
            command_0 = LabelSetLifecycleRenewLabelSet0Command(
                context=request.context,
                access_policy_owner_email=request.details.notify_contact.email,
                access_policy_owner_display_name=request.details.new_owner.display_name,
                access_policy_owner_user_id=request.details.new_owner.user_id,
                access_policy_block_reason=request.reason
            )
            outgoing_0 = to_label_set_lifecycle_renew_label_set0_command(command_0)
            response_0 = await deps.clients.authorization_access_policy.UpdateAccessPolicy(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.access_policy.name
            returned_0_0_part_1 = response.label_set.children.add()
            if returned_0_0:
                returned_0_0_part_1.name = returned_0_0
            returned_0_1 = response_0.access_policy.audit.updated_by
            returned_0_1_part_1 = response.label_set.children.add()
            if returned_0_1:
                returned_0_1_part_1.audit.updated_by = returned_0_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_schedule_label_set_expiry(
        self,
        request: labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryRequest
    ) -> labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryResponse:
        """Schedules a label set."""
        deps = self.deps
        response = labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleLabelSetExpiry', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScheduleLabelSetExpiry', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationResponse()
            command_0 = LabelSetLifecycleScheduleLabelSetExpiry0Command.model_validate(
                {
                    'context': request.context,
                    'details_contact_name': request.details.notify.name,
                    'customer_relationship_manager_display_name': request.label_set.manager.display_name,
                    'details_contact_preferred_channel': request.details.notify.preferred_channel
                }
            )
            outgoing_0 = to_label_set_lifecycle_schedule_label_set_expiry0_command(command_0)
            response_0 = await deps.clients.customers_customer_calculation.ExplainCustomerCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.customer.audit.etag
            returned_0_1_part_1 = response.label_set.children.add()
            if returned_0_1:
                returned_0_1_part_1.audit.etag = returned_0_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.location
            response.label_set.location.CopyFrom(echoed_1)
            return response

    async def handle_suspend_label_set(
        self,
        request: labeling_v1_label_set_lifecycle_service_pb2.SuspendLabelSetRequest
    ) -> labeling_v1_label_set_lifecycle_service_pb2.SuspendLabelSetResponse:
        """Suspends a label set."""
        deps = self.deps
        response = labeling_v1_label_set_lifecycle_service_pb2.SuspendLabelSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendLabelSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SuspendLabelSet', {'reason': request.reason})
            response_0 = labeling_v1_label_set_validation_service_pb2.PreviewLabelSetResponse()
            response_1 = labeling_v1_label_set_calculation_service_pb2.ExplainLabelSetCalculationResponse()
            response_2 = lineage_v1_lineage_edge_workflow_service_pb2.PauseLineageEdgeWorkflowResponse()
            outgoing_0 = labeling_v1_label_set_validation_service_pb2.PreviewLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.notify_contact.email)
                                )
                            ]
                        )
                    ]
                )
            )
            send_0 = partial(deps.clients.labeling_label_set_validation.PreviewLabelSet, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            outgoing_1 = labeling_v1_label_set_calculation_service_pb2.ExplainLabelSetCalculationRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    children=[labeling_v1_labeling_pb2.LabelSet(status=response_0.label_set.status)],
                                    location=common_v1_address_pb2.PostalAddress(
                                        postal_code=response_0.label_set.location.postal_code,
                                        recipient=response_0.label_set.location.recipient
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.label_set.manager.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = await hooks.label_set_lifecycle_suspend_label_set1(
                deps.clients.labeling_label_set_calculation,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = lineage_v1_lineage_edge_workflow_service_pb2.PauseLineageEdgeWorkflowRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.lineage_edge.subject.display_name = response_1.label_set.manager.display_name
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.lineage_lineage_edge_workflow.PauseLineageEdgeWorkflow(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.label_set.depth
            returned_0_0_part_1 = response.label_set.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            if returned_0_0:
                returned_0_0_part_2.depth = returned_0_0
            returned_0_1 = response_0.label_set.location.region
            returned_0_1_part_1 = response.label_set.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            if returned_0_1:
                returned_0_1_part_2.location.region = returned_0_1
            returned_1_0 = response_1.label_set.audit.created_at
            returned_1_0_part_1 = response.label_set.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            if returned_1_0.ListFields():
                returned_1_0_part_2.audit.created_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_0)
            returned_2_1 = response_2.lineage_edge.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_label_set(
        self,
        request: labeling_v1_label_set_lifecycle_service_pb2.TerminateLabelSetRequest
    ) -> labeling_v1_label_set_lifecycle_service_pb2.TerminateLabelSetResponse:
        """Terminates a label set."""
        deps = self.deps
        response = labeling_v1_label_set_lifecycle_service_pb2.TerminateLabelSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminateLabelSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TerminateLabelSet', {'reason': request.reason})
            response_0 = identity_v1_user_query_service_pb2.BrowseUsersResponse()
            response_1 = labeling_v1_label_set_reporting_service_pb2.ShareLabelSetReportResponse()
            outgoing_0 = identity_v1_user_query_service_pb2.BrowseUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.BrowseUsersRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.annotations),
                    owner_id=request.details.new_owner.user_id
                )
            )
            port_0: LabelSetLifecycleTerminateLabelSet0Port = LabelSetLifecycleTerminateLabelSet0Adapter(
                deps.clients.identity_user_query,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = labeling_v1_label_set_reporting_service_pb2.ShareLabelSetReportRequest(
                context=request.context,
                details=labeling_v1_label_set_reporting_service_pb2.ShareLabelSetReportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify_contact.email,
                        phone=request.details.notify_contact.phone,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.labeling_label_set_reporting.ShareLabelSetReport,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.label_set.label_set_id
            returned_1_1_part_1 = response.label_set.children.add()
            if returned_1_1:
                returned_1_1_part_1.label_set_id = returned_1_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
