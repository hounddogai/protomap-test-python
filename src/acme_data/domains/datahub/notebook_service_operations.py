"""Functional operations behind NotebookService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage

from acme.analytics.v1 import funnel_workflow_service_pb2 as analytics_v1_funnel_workflow_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_segment_sync_service_pb2 as customers_v1_customer_segment_sync_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_reporting_service_pb2 as customers_v1_preference_reporting_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_reporting_service_pb2 as datahub_v1_notebook_reporting_service_pb2
from acme.datahub.v1 import notebook_service_pb2 as datahub_v1_notebook_service_pb2
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import workspace_notification_service_pb2 as datahub_v1_workspace_notification_service_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2 as datahub_v1_workspace_reporting_service_pb2
from acme.datahub.v1 import workspace_workflow_service_pb2 as datahub_v1_workspace_workflow_service_pb2
from acme.edgegateway.v1 import edgegateway_pb2 as edgegateway_v1_edgegateway_pb2
from acme.edgegateway.v1 import route_binding_service_pb2 as edgegateway_v1_route_binding_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_workflow_service_pb2 as forecasting_v1_demand_forecast_workflow_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_approval_service_pb2 as labeling_v1_label_set_approval_service_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.modelregistry.v1 import deployment_approval_service_pb2 as modelregistry_v1_deployment_approval_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.patientapp.v1 import patient_home_service_pb2 as patientapp_v1_patient_home_service_pb2
from acme.recommendations.v1 import (
    interaction_workflow_service_pb2 as recommendations_v1_interaction_workflow_service_pb2,
)
from acme.telehealth.v1 import video_visit_calculation_service_pb2 as telehealth_v1_video_visit_calculation_service_pb2

from acme_data.domains.datahub.adapters import NotebookWatchNotebooks1Adapter
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import NotebookDeleteNotebook1Command
from acme_data.domains.datahub.models import NotebookDeleteNotebook2Command
from acme_data.domains.datahub.models import to_notebook_delete_notebook1_command
from acme_data.domains.datahub.models import to_notebook_delete_notebook2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_batch_create_notebooks(
    deps: Dependencies,
    request: datahub_v1_notebook_service_pb2.BatchCreateNotebooksRequest
) -> datahub_v1_notebook_service_pb2.BatchCreateNotebooksResponse:
    """Takes a stream of notebooks and answers once at the end."""
    response = datahub_v1_notebook_service_pb2.BatchCreateNotebooksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BatchCreateNotebooks', extra={'fields': {'sequence': request.sequence}})
        await deps.repository.audit(request.context.tenant_id, 'BatchCreateNotebooks', {'sequence': request.sequence})
        if request.WhichOneof('chunk') == 'record':
            await deps.repository.save_notebook(request.context.tenant_id, request.record)
        response_0 = patientapp_v1_patient_home_service_pb2.BatchGetPatientHomesResponse()
        response_1 = datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsResponse()
        outgoing_0 = patientapp_v1_patient_home_service_pb2.BatchGetPatientHomesRequest(context=request.context)
        response_0 = await deps.clients.patientapp_patient_home.BatchGetPatientHomes(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(
                email=request.header.submitted_by.email,
                phone=request.header.submitted_by.phone,
                preferred_channel=request.header.submitted_by.preferred_channel
            )
        )
        async for chunk_1 in deps.clients.datahub_notebook_reporting.StreamNotebookMetrics(
            outgoing_1,
            timeout=deps.settings.timeout
        ):
            response_1 = chunk_1
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        return response


async def handle_clone_notebook(
    deps: Dependencies,
    request: datahub_v1_notebook_service_pb2.CloneNotebookRequest
) -> datahub_v1_notebook_service_pb2.CloneNotebookResponse:
    """Creates a notebook."""
    response = datahub_v1_notebook_service_pb2.CloneNotebookResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CloneNotebook', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(request.context.tenant_id, 'CloneNotebook', {'request_id': request.request_id})
        await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
        response_0 = datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportResponse()
        response_1 = datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowResponse()
        response_2 = customers_v1_customer_segment_sync_service_pb2.PushCustomerSegmentResponse()
        response_3 = datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeResponse()
        outgoing_0 = datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportRequest(
            context=request.context,
            details=datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportRequest.Details(
                recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            ),
            workspace_id=request.notebook.counterparty.workspace_id
        )
        response_0 = await deps.clients.datahub_workspace_reporting.ShareWorkspaceReport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        fields_1: dict[str, Any] = {
            'context': request.context,
            'workspace': {
                'audit': {'updated_by': response_0.workspace.audit.updated_by},
                'customer': {'display_name': response_0.workspace.customer.display_name}
            }
        }
        outgoing_1 = datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowRequest(**fields_1)
        response_1 = await deps.clients.datahub_workspace_workflow.AdvanceWorkspaceWorkflow(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        for item_2 in request.notebook.lines:
            outgoing_2 = customers_v1_customer_segment_sync_service_pb2.PushCustomerSegmentRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    description=item_2.description,
                    discount=customers_v1_customers_pb2.CustomerSegmentDiscountAction(amount=item_2.tax.amount),
                    owner=identity_v1_refs_pb2.UserRef(email=response_1.workspace.assignee.email)
                )
            )
            response_2 = await deps.clients.customers_customer_segment_sync.PushCustomerSegment(
                outgoing_2,
                timeout=deps.settings.timeout
            )
        outgoing_3 = datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeRequest()
        outgoing_3.context.CopyFrom(request.context)
        if response_0.workspace.WhichOneof('origin') == 'customer':
            outgoing_3.details.recipient.email = response_0.workspace.customer.email
        if response_1.workspace.WhichOneof('origin') == 'channel':
            outgoing_3.details.channel = response_1.workspace.channel.channel
        outgoing_3.details.recipient.name.CopyFrom(response_1.workspace.requester.name)
        response_3 = await deps.clients.datahub_workspace_notification.SendWorkspaceTestNotice(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.workspace.customer.display_name
        if returned_0_0:
            response.notebook.counterparty.display_name = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.workspace.workspace_id
        if returned_1_1:
            response.notebook.counterparty.workspace_id = returned_1_1
        returned_3_0 = response_3.workspace.sla.due_at
        if returned_3_0.ListFields():
            response.notebook.due_at.MergeFrom(returned_3_0)
        returned_3_1 = response_3.workspace.audit.updated_by
        if returned_3_1:
            response.notebook.audit.updated_by = returned_3_1
        echoed_0 = request.notebook.billing_address
        response.notebook.billing_address.CopyFrom(echoed_0)
        echoed_1 = request.notebook.total
        response.notebook.total.CopyFrom(echoed_1)
        return response


async def handle_create_notebook(
    deps: Dependencies,
    request: datahub_v1_notebook_service_pb2.CreateNotebookRequest
) -> datahub_v1_notebook_service_pb2.CreateNotebookResponse:
    """Creates a notebook."""
    response = datahub_v1_notebook_service_pb2.CreateNotebookResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CreateNotebook', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(request.context.tenant_id, 'CreateNotebook', {'request_id': request.request_id})
        await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
        response_0 = edgegateway_v1_route_binding_service_pb2.CloneRouteBindingResponse()
        response_1 = datahub_v1_data_share_validation_service_pb2.PreviewDataShareResponse()
        outgoing_0 = edgegateway_v1_route_binding_service_pb2.CloneRouteBindingRequest(
            context=request.context,
            route_binding=edgegateway_v1_edgegateway_pb2.RouteBinding(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=request.notebook.audit.created_at,
                    updated_at=request.notebook.audit.updated_at
                ),
                owner=identity_v1_refs_pb2.UserRef(display_name=request.notebook.counterparty.display_name)
            )
        )
        response_0 = await deps.clients.edgegateway_route_binding.CloneRouteBinding(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = datahub_v1_data_share_validation_service_pb2.PreviewDataShareRequest(
            context=request.context,
            data_share=datahub_v1_datahub_pb2.DataShare(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=response_0.route_binding.audit.created_at,
                    etag=request.notebook.audit.etag
                ),
                billing_address=common_v1_address_pb2.PostalAddress(lines=list(request.notebook.billing_address.lines)),
                lines=[
                    datahub_v1_datahub_pb2.DataShareLine(
                        tax=datahub_v1_datahub_pb2.DataShareLineTax(amount=response_0.route_binding.discount.amount)
                    )
                ]
            )
        )
        envelope_1 = AnyMessage()
        envelope_1.Pack(outgoing_1)
        outgoing_1 = datahub_v1_data_share_validation_service_pb2.PreviewDataShareRequest()
        if not envelope_1.Unpack(outgoing_1):
            raise ValueError("partner envelope contains the wrong request type")
        response_1 = await deps.clients.datahub_data_share_validation.PreviewDataShare(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.route_binding.audit.etag
        if returned_0_0:
            response.notebook.audit.etag = returned_0_0
        returned_1_0 = response_1.data_share.billing_address
        if returned_1_0.ListFields():
            response.notebook.billing_address.MergeFrom(returned_1_0)
        echoed_0 = request.notebook.notes
        response.notebook.notes = echoed_0
        echoed_1 = request.notebook.due_at
        response.notebook.due_at.CopyFrom(echoed_1)
        return response


async def handle_delete_notebook(
    deps: Dependencies,
    request: datahub_v1_notebook_service_pb2.DeleteNotebookRequest
) -> datahub_v1_notebook_service_pb2.DeleteNotebookResponse:
    """Deletes a notebook."""
    response = datahub_v1_notebook_service_pb2.DeleteNotebookResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('DeleteNotebook', extra={'fields': {'force': request.force}})
        await deps.repository.audit(request.context.tenant_id, 'DeleteNotebook', {'force': request.force})
        response_0 = recommendations_v1_interaction_workflow_service_pb2.ListInteractionWorkflowsResponse()
        response_1 = labeling_v1_label_set_approval_service_pb2.RejectLabelSetResponse()
        response_2 = forecasting_v1_demand_forecast_workflow_service_pb2.CancelDemandForecastWorkflowResponse()
        response_3 = customers_v1_preference_reporting_service_pb2.SchedulePreferenceReportResponse()
        outgoing_0 = recommendations_v1_interaction_workflow_service_pb2.ListInteractionWorkflowsRequest(
            context=request.context,
            filter=recommendations_v1_interaction_workflow_service_pb2.ListInteractionWorkflowsRequest.Filter(
                created_after=request.context.deadline,
                labels=dict(request.context.baggage),
                owner_id=request.notebook_id
            )
        )
        response_0 = await deps.clients.recommendations_interaction_workflow.ListInteractionWorkflows(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = NotebookDeleteNotebook1Command(
            context=request.context,
            label_set_children_children_audit_etag=request.etag
        )
        outgoing_1 = to_notebook_delete_notebook1_command(command_1)
        response_1 = await deps.clients.labeling_label_set_approval.RejectLabelSet(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        command_2 = NotebookDeleteNotebook2Command.model_validate(
            {
                'context': request.context,
                'demand_forecast_billing_address_lines': list(response_1.label_set.location.lines),
                'demand_forecast_billing_address_recipient': response_1.label_set.location.recipient,
                'demand_forecast_audit_created_at': response_1.label_set.audit.created_at
            }
        )
        outgoing_2 = to_notebook_delete_notebook2_command(command_2)
        response_2 = await deps.clients.forecasting_demand_forecast_workflow.CancelDemandForecastWorkflow(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = customers_v1_preference_reporting_service_pb2.SchedulePreferenceReportRequest(
            context=request.context,
            details=customers_v1_preference_reporting_service_pb2.SchedulePreferenceReportRequest.Details(
                filters=dict(response_2.result.details)
            ),
            reason=request.reason
        )
        send_3 = partial(
            deps.clients.customers_preference_reporting.SchedulePreferenceReport,
            timeout=deps.settings.timeout
        )
        response_3 = await send_3(outgoing_3)
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_2_0 = response_2.outcome.status
        if returned_2_0:
            response.result.status = returned_2_0
        returned_3_0 = response_3.result.reference_ids
        response.result.reference_ids.extend(returned_3_0)
        return response


async def handle_get_notebook(
    deps: Dependencies,
    request: datahub_v1_notebook_service_pb2.GetNotebookRequest
) -> datahub_v1_notebook_service_pb2.GetNotebookResponse:
    """Returns a notebook."""
    response = datahub_v1_notebook_service_pb2.GetNotebookResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetNotebook', extra={'fields': {'locale': request.context.locale}})
        await deps.repository.audit(request.context.tenant_id, 'GetNotebook', {'locale': request.context.locale})
        echoed_0 = request.notebook_id
        response.notebook.notebook_id = echoed_0
        return response


async def handle_list_notebooks(
    deps: Dependencies,
    request: datahub_v1_notebook_service_pb2.ListNotebooksRequest
) -> datahub_v1_notebook_service_pb2.ListNotebooksResponse:
    """Lists notebooks a page at a time."""
    response = datahub_v1_notebook_service_pb2.ListNotebooksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListNotebooks', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListNotebooks', {'order_by': request.order_by})
        return response


async def handle_update_notebook(
    deps: Dependencies,
    request: datahub_v1_notebook_service_pb2.UpdateNotebookRequest
) -> datahub_v1_notebook_service_pb2.UpdateNotebookResponse:
    """Changes a notebook."""
    response = datahub_v1_notebook_service_pb2.UpdateNotebookResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('UpdateNotebook', extra={'fields': {'allow_missing': request.allow_missing}})
        await deps.repository.audit(
            request.context.tenant_id,
            'UpdateNotebook',
            {'allow_missing': request.allow_missing}
        )
        await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
        response_0 = datahub_v1_workspace_notification_service_pb2.UnsubscribeWorkspaceUpdatesResponse()
        response_1 = telehealth_v1_video_visit_calculation_service_pb2.CalculateVideoVisitResponse()
        response_2 = datahub_v1_workspace_workflow_service_pb2.ResumeWorkspaceWorkflowResponse()
        outgoing_0 = datahub_v1_workspace_notification_service_pb2.UnsubscribeWorkspaceUpdatesRequest(
            context=request.context,
            details=datahub_v1_workspace_notification_service_pb2.UnsubscribeWorkspaceUpdatesRequest.Details(
                recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                variables=dict(request.notebook.metadata)
            ),
            workspace_id=request.notebook.counterparty.workspace_id
        )
        response_0 = await deps.clients.datahub_workspace_notification.UnsubscribeWorkspaceUpdates(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = telehealth_v1_video_visit_calculation_service_pb2.CalculateVideoVisitRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.details.destination.lines.extend(list(request.notebook.billing_address.lines))
        outgoing_1.context.tenant_id = tenant_id.get()
        response_1 = await deps.clients.telehealth_video_visit_calculation.CalculateVideoVisit(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = datahub_v1_workspace_workflow_service_pb2.ResumeWorkspaceWorkflowRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.workspace.sla.policy_id = response_0.workspace.sla.policy_id
        if response_0.workspace.WhichOneof('origin') == 'customer':
            outgoing_2.workspace.assignee.email = response_0.workspace.customer.email
        response_2 = await deps.clients.datahub_workspace_workflow.ResumeWorkspaceWorkflow(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.workspace.sla.due_at
        if returned_0_0.ListFields():
            response.notebook.due_at.MergeFrom(returned_0_0)
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        returned_1_1 = response_1.video_visit.location.country_code
        if returned_1_1:
            response.notebook.billing_address.country_code = returned_1_1
        returned_2_0 = response_2.workspace.sla.due_at
        if returned_2_0.ListFields():
            response.notebook.due_at.MergeFrom(returned_2_0)
        echoed_0 = request.notebook.metadata
        response.notebook.metadata.update(echoed_0)
        echoed_1 = request.notebook.notes
        response.notebook.notes = echoed_1
        return response


async def handle_watch_notebooks(
    deps: Dependencies,
    request: datahub_v1_notebook_service_pb2.WatchNotebooksRequest
) -> datahub_v1_notebook_service_pb2.WatchNotebooksResponse:
    """Streams the changes of notebooks as they happen."""
    response = datahub_v1_notebook_service_pb2.WatchNotebooksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('WatchNotebooks', extra={'fields': {'max_events': request.max_events}})
        await deps.repository.audit(request.context.tenant_id, 'WatchNotebooks', {'max_events': request.max_events})
        response_0 = datahub_v1_notebook_workflow_service_pb2.ListNotebookWorkflowsResponse()
        response_1 = metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionResponse()
        response_2 = analytics_v1_funnel_workflow_service_pb2.RetryFunnelWorkflowResponse()
        response_3 = modelregistry_v1_deployment_approval_service_pb2.RejectDeploymentResponse()
        outgoing_0 = datahub_v1_notebook_workflow_service_pb2.ListNotebookWorkflowsRequest(
            context=request.context,
            filter=datahub_v1_notebook_workflow_service_pb2.ListNotebookWorkflowsRequest.Filter(
                created_after=request.filter.created_after,
                query=request.filter.query,
                region=request.filter.region,
                statuses=list(request.filter.statuses)
            )
        )
        response_0 = await deps.clients.datahub_notebook_workflow.ListNotebookWorkflows(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionRequest(
            context=request.context,
            details=metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(preferred_channel=request.subscriber.preferred_channel)
            )
        )
        response_1 = await NotebookWatchNotebooks1Adapter(
            deps.clients.metrics_metric_alert_validation,
            deps.settings.timeout
        )(outgoing_1)
        outgoing_2 = analytics_v1_funnel_workflow_service_pb2.RetryFunnelWorkflowRequest()
        outgoing_2.context.CopyFrom(request.context)
        if response_1.metric_alert.WhichOneof('action') == 'discount':
            outgoing_2.funnel.discount.percent = response_1.metric_alert.discount.percent
        response_2 = await deps.clients.analytics_funnel_workflow.RetryFunnelWorkflow(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = modelregistry_v1_deployment_approval_service_pb2.RejectDeploymentRequest(
            context=request.context,
            deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=response_1.metric_alert.audit.updated_at),
                organizer=identity_v1_refs_pb2.UserRef(
                    email=response_2.funnel.owner.email,
                    user_id=response_2.funnel.owner.user_id
                ),
                participants=[
                    modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(email=response_1.metric_alert.owner.email)
                    )
                ]
            )
        )
        response_3 = await deps.clients.modelregistry_deployment_approval.RejectDeployment(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.result.correlation_id = returned_0_1
        returned_1_0 = response_1.metric_alert.description
        returned_1_0_part_1 = response.notebook.lines.add()
        if returned_1_0:
            returned_1_0_part_1.description = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        returned_2_0 = response_2.funnel.audit.created_by
        if returned_2_0:
            response.notebook.audit.created_by = returned_2_0
        returned_3_0 = response_3.deployment.location.lines
        response.notebook.billing_address.lines.extend(returned_3_0)
        echoed_0 = request.filter.region
        response.notebook.billing_address.region = echoed_0
        return response
