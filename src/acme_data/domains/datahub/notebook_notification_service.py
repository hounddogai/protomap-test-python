"""Tells the people who follow a notebook what changed."""

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

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_approval_service_pb2 as customers_v1_customer_approval_service_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import data_share_workflow_service_pb2 as datahub_v1_data_share_workflow_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_notification_service_pb2 as datahub_v1_notebook_notification_service_pb2
from acme.datahub.v1 import notebook_notification_service_pb2_grpc as datahub_v1_notebook_notification_service_pb2_grpc
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import refs_pb2 as datahub_v1_refs_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2 as datahub_v1_workspace_reporting_service_pb2
from acme.datasets.v1 import dataset_workflow_service_pb2 as datasets_v1_dataset_workflow_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.pipelines.v1 import pipeline_run_workflow_service_pb2 as pipelines_v1_pipeline_run_workflow_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import NotebookNotificationSendNotebookTestNotice1Adapter
from acme_data.domains.datahub.adapters import NotebookNotificationSendNotebookTestNotice1Port
from acme_data.domains.datahub.adapters import NotebookNotificationStreamNotebookNotices1Adapter
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import NotebookNotificationNotifyNotebookWatchers0Command
from acme_data.domains.datahub.models import to_notebook_notification_notify_notebook_watchers0_command
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class NotebookNotificationServicer(
    datahub_v1_notebook_notification_service_pb2_grpc.NotebookNotificationServiceServicer
):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def GetNotebookPreferences(
        self, request: datahub_v1_notebook_notification_service_pb2.GetNotebookPreferencesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_notification_service_pb2.GetNotebookPreferencesResponse:
        """Returns a notebook."""
        return await self.handle_get_notebook_preferences(request)

    @rpc_errors
    @retry_transient
    async def ListNotebookSubscriptions(
        self, request: datahub_v1_notebook_notification_service_pb2.ListNotebookSubscriptionsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_notification_service_pb2.ListNotebookSubscriptionsResponse:
        """Lists notebooks a page at a time."""
        return await self.handle_list_notebook_subscriptions(request)

    @rpc_errors
    async def NotifyNotebookWatchers(
        self, request: datahub_v1_notebook_notification_service_pb2.NotifyNotebookWatchersRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_notification_service_pb2.NotifyNotebookWatchersResponse:
        """Notifys a notebook."""
        return await self.handle_notify_notebook_watchers(request)

    @rpc_errors
    async def SendNotebookTestNotice(
        self, request: datahub_v1_notebook_notification_service_pb2.SendNotebookTestNoticeRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_notification_service_pb2.SendNotebookTestNoticeResponse:
        """Sends a notebook."""
        return await self.handle_send_notebook_test_notice(request)

    @stream_errors
    async def StreamNotebookNotices(
        self, request: datahub_v1_notebook_notification_service_pb2.StreamNotebookNoticesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_notebook_notification_service_pb2.StreamNotebookNoticesResponse]:
        """Streams the changes of notebooks as they happen."""
        response = await self.handle_stream_notebook_notices(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    async def SubscribeNotebookUpdates(
        self, request: datahub_v1_notebook_notification_service_pb2.SubscribeNotebookUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_notification_service_pb2.SubscribeNotebookUpdatesResponse:
        """Subscribes a notebook."""
        return await self.handle_subscribe_notebook_updates(request)

    @rpc_errors
    async def UnsubscribeNotebookUpdates(
        self, request: datahub_v1_notebook_notification_service_pb2.UnsubscribeNotebookUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_notification_service_pb2.UnsubscribeNotebookUpdatesResponse:
        """Unsubscribes a notebook."""
        return await self.handle_unsubscribe_notebook_updates(request)

    async def handle_get_notebook_preferences(
        self,
        request: datahub_v1_notebook_notification_service_pb2.GetNotebookPreferencesRequest
    ) -> datahub_v1_notebook_notification_service_pb2.GetNotebookPreferencesResponse:
        """Returns a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_notification_service_pb2.GetNotebookPreferencesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetNotebookPreferences', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetNotebookPreferences',
                {'locale': request.context.locale}
            )
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response

    async def handle_list_notebook_subscriptions(
        self,
        request: datahub_v1_notebook_notification_service_pb2.ListNotebookSubscriptionsRequest
    ) -> datahub_v1_notebook_notification_service_pb2.ListNotebookSubscriptionsResponse:
        """Lists notebooks a page at a time."""
        deps = self.deps
        response = datahub_v1_notebook_notification_service_pb2.ListNotebookSubscriptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListNotebookSubscriptions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListNotebookSubscriptions',
                {'order_by': request.order_by}
            )
            response_0 = datahub_v1_data_share_approval_service_pb2.EscalateDataShareResponse()
            outgoing_0 = datahub_v1_data_share_approval_service_pb2.EscalateDataShareRequest(
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.datahub_data_share_approval.EscalateDataShare(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.data_share.notes
            returned_0_0_part_0 = response.notebooks.add()
            if returned_0_0:
                returned_0_0_part_0.notes = returned_0_0
            return response

    async def handle_notify_notebook_watchers(
        self,
        request: datahub_v1_notebook_notification_service_pb2.NotifyNotebookWatchersRequest
    ) -> datahub_v1_notebook_notification_service_pb2.NotifyNotebookWatchersResponse:
        """Notifys a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_notification_service_pb2.NotifyNotebookWatchersResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NotifyNotebookWatchers', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NotifyNotebookWatchers', {'reason': request.reason})
            response_0 = datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowResponse()
            response_1 = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionResponse()
            response_2 = datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowResponse()
            command_0 = NotebookNotificationNotifyNotebookWatchers0Command.model_validate(
                {
                    'context': request.context,
                    'details_notify_name': request.details.recipient.name,
                    'details_notify_email': request.details.recipient.email,
                    'details_notify_phone': request.details.recipient.phone,
                    'notebook_notebook_id': request.notebook_id
                }
            )
            outgoing_0 = to_notebook_notification_notify_notebook_watchers0_command(command_0)
            response_0 = await deps.clients.datahub_notebook_workflow.SignalNotebookWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.notebook.billing_address.country_code
                    )
                )
            )
            send_1 = partial(
                deps.clients.metrics_dashboard_validation.ExplainDashboardDecision,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowRequest(
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.notebook.audit.etag),
                    bank=datahub_v1_datahub_pb2.DataShareBankSettlement(iban=response_1.dashboard.bank.iban),
                    counterparty=datahub_v1_refs_pb2.NotebookRef(
                        display_name=response_0.notebook.counterparty.display_name
                    )
                ),
                details=datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.recipient.preferred_channel
                    )
                )
            )
            response_2 = await hooks.notebook_notification_notify_notebook_watchers2(
                deps.clients.datahub_data_share_workflow,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.notebook.metadata
            response.notebook.metadata.update(returned_0_0)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_2_0 = response_2.data_share.billing_address
            if returned_2_0.ListFields():
                response.notebook.billing_address.MergeFrom(returned_2_0)
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response

    async def handle_send_notebook_test_notice(
        self,
        request: datahub_v1_notebook_notification_service_pb2.SendNotebookTestNoticeRequest
    ) -> datahub_v1_notebook_notification_service_pb2.SendNotebookTestNoticeResponse:
        """Sends a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_notification_service_pb2.SendNotebookTestNoticeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SendNotebookTestNotice', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SendNotebookTestNotice', {'reason': request.reason})
            response_0 = datahub_v1_data_share_validation_service_pb2.ValidateDataShareResponse()
            response_1 = pipelines_v1_pipeline_run_workflow_service_pb2.StartPipelineRunWorkflowResponse()
            outgoing_0 = datahub_v1_data_share_validation_service_pb2.ValidateDataShareRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.contact.preferred_channel = request.details.recipient.preferred_channel
            outgoing_0.details.contact.email = request.details.recipient.email
            outgoing_0.details.contact.name.CopyFrom(request.details.recipient.name)
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.datahub_data_share_validation.ValidateDataShare(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_run_workflow_service_pb2.StartPipelineRunWorkflowRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=response_0.data_share.audit.etag,
                        updated_by=response_0.data_share.audit.updated_by
                    ),
                    requester=common_v1_contact_pb2.ContactInfo(
                        email=request.details.recipient.email,
                        name=request.details.recipient.name
                    )
                )
            )
            port_1: NotebookNotificationSendNotebookTestNotice1Port = NotebookNotificationSendNotebookTestNotice1Adapter(
                deps.clients.pipelines_pipeline_run_workflow,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.pipeline_run.audit.etag
            if returned_1_0:
                response.notebook.audit.etag = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response

    async def handle_stream_notebook_notices(
        self,
        request: datahub_v1_notebook_notification_service_pb2.StreamNotebookNoticesRequest
    ) -> datahub_v1_notebook_notification_service_pb2.StreamNotebookNoticesResponse:
        """Streams the changes of notebooks as they happen."""
        deps = self.deps
        response = datahub_v1_notebook_notification_service_pb2.StreamNotebookNoticesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamNotebookNotices', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamNotebookNotices',
                {'max_events': request.max_events}
            )
            response_0 = venues_v1_venue_service_pb2.CloneVenueResponse()
            response_1 = customers_v1_customer_approval_service_pb2.ListPendingCustomersResponse()
            outgoing_0 = venues_v1_venue_service_pb2.CloneVenueRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.subscriber.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            steps_0 = [partial(deps.clients.venues_venue.CloneVenue, outgoing_0, timeout=deps.settings.timeout)]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = customers_v1_customer_approval_service_pb2.ListPendingCustomersRequest(
                context=request.context,
                filter=customers_v1_customer_approval_service_pb2.ListPendingCustomersRequest.Filter(
                    region=request.filter.region
                )
            )
            response_1 = await NotebookNotificationStreamNotebookNotices1Adapter(
                deps.clients.customers_customer_approval,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.venue.address.locality
            if returned_0_0:
                response.notebook.billing_address.locality = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.filter.region
            response.notebook.billing_address.region = echoed_0
            return response

    async def handle_subscribe_notebook_updates(
        self,
        request: datahub_v1_notebook_notification_service_pb2.SubscribeNotebookUpdatesRequest
    ) -> datahub_v1_notebook_notification_service_pb2.SubscribeNotebookUpdatesResponse:
        """Subscribes a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_notification_service_pb2.SubscribeNotebookUpdatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubscribeNotebookUpdates', extra={'fields': {'notebook_id': request.notebook_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SubscribeNotebookUpdates',
                {'notebook_id': request.notebook_id}
            )
            response_0 = datahub_v1_data_share_workflow_service_pb2.RetryDataShareWorkflowResponse()
            response_1 = datahub_v1_notebook_approval_service_pb2.SubmitNotebookResponse()
            outgoing_0 = datahub_v1_data_share_workflow_service_pb2.RetryDataShareWorkflowRequest(
                context=request.context,
                details=datahub_v1_data_share_workflow_service_pb2.RetryDataShareWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.details.recipient.email)
                )
            )
            response_0 = cast(datahub_v1_data_share_workflow_service_pb2.RetryDataShareWorkflowResponse, await deps.bus.request(
                'acme.datahub.v1.NotebookNotificationService/SubscribeNotebookUpdates/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = datahub_v1_notebook_approval_service_pb2.SubmitNotebookRequest(
                context=request.context,
                notebook=datahub_v1_datahub_pb2.Notebook(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.data_share.audit.created_at),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        lines=list(response_0.data_share.billing_address.lines),
                        locality=response_0.data_share.billing_address.locality
                    ),
                    card=datahub_v1_datahub_pb2.NotebookCardSettlement(
                        holder_name=response_0.data_share.card.holder_name
                    )
                )
            )
            response_1 = await deps.clients.datahub_notebook_approval.SubmitNotebook(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.data_share.counterparty.notebook_id
            if returned_0_0:
                response.notebook.notebook_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            return response

    async def handle_unsubscribe_notebook_updates(
        self,
        request: datahub_v1_notebook_notification_service_pb2.UnsubscribeNotebookUpdatesRequest
    ) -> datahub_v1_notebook_notification_service_pb2.UnsubscribeNotebookUpdatesResponse:
        """Unsubscribes a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_notification_service_pb2.UnsubscribeNotebookUpdatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UnsubscribeNotebookUpdates', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'UnsubscribeNotebookUpdates',
                {'reason': request.reason}
            )
            response_0 = datasets_v1_dataset_workflow_service_pb2.PauseDatasetWorkflowResponse()
            response_1 = venues_v1_venue_service_pb2.CloneVenueResponse()
            response_2 = datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsResponse()
            outgoing_0 = datasets_v1_dataset_workflow_service_pb2.PauseDatasetWorkflowRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.recipient.email)
                ),
                details=datasets_v1_dataset_workflow_service_pb2.PauseDatasetWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        name=request.details.recipient.name,
                        phone=request.details.recipient.phone
                    )
                )
            )
            method_name_0 = 'PauseDatasetWorkflow'
            response_0 = await getattr(
                deps.clients.datasets_dataset_workflow,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'venue': {'owner': {'user_id': response_0.dataset.owner.user_id}}
            }
            outgoing_1 = venues_v1_venue_service_pb2.CloneVenueRequest(**fields_1)
            response_1 = await deps.clients.venues_venue.CloneVenue(outgoing_1, timeout=deps.settings.timeout)
            outgoing_2 = datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsRequest(
                context=request.context,
                filter=datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsRequest.Filter(
                    region=response_1.venue.address.region
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(document_2, datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsRequest())
            response_2 = await deps.clients.datahub_workspace_reporting.ListWorkspaceReports(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset.audit.etag
            if returned_0_0:
                response.notebook.audit.etag = returned_0_0
            returned_1_0 = response_1.venue.address.country_code
            if returned_1_0:
                response.notebook.billing_address.country_code = returned_1_0
            returned_1_1 = response_1.venue.audit.updated_at
            if returned_1_1.ListFields():
                response.notebook.audit.updated_at.MergeFrom(returned_1_1)
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response
