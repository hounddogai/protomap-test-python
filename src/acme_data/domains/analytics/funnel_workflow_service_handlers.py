"""Reusable transport mixin for FunnelWorkflowService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.analytics.v1 import analytics_event_workflow_service_pb2 as analytics_v1_analytics_event_workflow_service_pb2
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import funnel_workflow_service_pb2 as analytics_v1_funnel_workflow_service_pb2
from acme.analytics.v1 import refs_pb2 as analytics_v1_refs_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import dataset_version_workflow_service_pb2 as datasets_v1_dataset_version_workflow_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_reporting_service_pb2 as labeling_v1_annotation_reporting_service_pb2
from acme.labeling.v1 import label_set_approval_service_pb2 as labeling_v1_label_set_approval_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.yards.v1 import yard_query_service_pb2 as yards_v1_yard_query_service_pb2

from acme_data.domains.analytics import hooks
from acme_data.domains.analytics.adapters import FunnelWorkflowStartFunnelWorkflow1Adapter
from acme_data.domains.analytics.adapters import FunnelWorkflowStartFunnelWorkflow1Port
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FunnelWorkflowServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceFunnelWorkflow(
        self, request: analytics_v1_funnel_workflow_service_pb2.AdvanceFunnelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_workflow_service_pb2.AdvanceFunnelWorkflowResponse:
        """Advances a funnel."""
        return await self.handle_advance_funnel_workflow(request)

    @rpc_errors
    async def CancelFunnelWorkflow(
        self, request: analytics_v1_funnel_workflow_service_pb2.CancelFunnelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_workflow_service_pb2.CancelFunnelWorkflowResponse:
        """Cancels a funnel."""
        return await self.handle_cancel_funnel_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectFunnelWorkflow(
        self, request: analytics_v1_funnel_workflow_service_pb2.InspectFunnelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_workflow_service_pb2.InspectFunnelWorkflowResponse:
        """Returns a funnel."""
        return await self.handle_inspect_funnel_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListFunnelWorkflows(
        self, request: analytics_v1_funnel_workflow_service_pb2.ListFunnelWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_workflow_service_pb2.ListFunnelWorkflowsResponse:
        """Lists funnels a page at a time."""
        return await self.handle_list_funnel_workflows(request)

    @rpc_errors
    async def ResumeFunnelWorkflow(
        self, request: analytics_v1_funnel_workflow_service_pb2.ResumeFunnelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_workflow_service_pb2.ResumeFunnelWorkflowResponse:
        """Resumes a funnel."""
        return await self.handle_resume_funnel_workflow(request)

    @rpc_errors
    async def RetryFunnelWorkflow(
        self, request: analytics_v1_funnel_workflow_service_pb2.RetryFunnelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_workflow_service_pb2.RetryFunnelWorkflowResponse:
        """Retrys a funnel."""
        return await self.handle_retry_funnel_workflow(request)

    @rpc_errors
    async def SignalFunnelWorkflow(
        self, request: analytics_v1_funnel_workflow_service_pb2.SignalFunnelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_workflow_service_pb2.SignalFunnelWorkflowResponse:
        """Signals a funnel."""
        return await self.handle_signal_funnel_workflow(request)

    @rpc_errors
    async def StartFunnelWorkflow(
        self, request: analytics_v1_funnel_workflow_service_pb2.StartFunnelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_workflow_service_pb2.StartFunnelWorkflowResponse:
        """Starts a funnel."""
        return await self.handle_start_funnel_workflow(request)

    async def handle_advance_funnel_workflow(
        self,
        request: analytics_v1_funnel_workflow_service_pb2.AdvanceFunnelWorkflowRequest
    ) -> analytics_v1_funnel_workflow_service_pb2.AdvanceFunnelWorkflowResponse:
        """Advances a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_workflow_service_pb2.AdvanceFunnelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceFunnelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'AdvanceFunnelWorkflow', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = customers_v1_preference_calculation_service_pb2.EstimatePreferenceResponse()
            response_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackResponse()
            outgoing_0 = customers_v1_preference_calculation_service_pb2.EstimatePreferenceRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.funnel.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.funnel.owner.display_name)
                )
            )
            response_0 = cast(customers_v1_preference_calculation_service_pb2.EstimatePreferenceResponse, await deps.bus.request(
                'acme.analytics.v1.FunnelWorkflowService/AdvanceFunnelWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest(
                context=request.context,
                details=anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=response_0.preference.owner.email)
                )
            )
            response_1 = await deps.clients.anomalies_anomaly_feedback_approval.SubmitAnomalyFeedback(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.preference.audit.etag
            if returned_0_0:
                response.funnel.audit.etag = returned_0_0
            returned_1_0 = response_1.outcome.reference_id
            if returned_1_0:
                response.outcome.reference_id = returned_1_0
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.description
            response.funnel.description = echoed_1
            return response

    async def handle_cancel_funnel_workflow(
        self,
        request: analytics_v1_funnel_workflow_service_pb2.CancelFunnelWorkflowRequest
    ) -> analytics_v1_funnel_workflow_service_pb2.CancelFunnelWorkflowResponse:
        """Cancels a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_workflow_service_pb2.CancelFunnelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelFunnelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CancelFunnelWorkflow', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = documents_v1_document_query_service_pb2.BrowseDocumentsResponse()
            outgoing_0 = documents_v1_document_query_service_pb2.BrowseDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_query_service_pb2.BrowseDocumentsRequest.Filter(
                    created_after=request.funnel.audit.created_at,
                    labels=dict(request.funnel.parameters),
                    owner_id=request.funnel.owner.user_id
                )
            )
            method_name_0 = 'BrowseDocuments'
            response_0 = await getattr(
                deps.clients.documents_document_query,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.details.parameters
            response.funnel.parameters.update(echoed_1)
            return response

    async def handle_inspect_funnel_workflow(
        self,
        request: analytics_v1_funnel_workflow_service_pb2.InspectFunnelWorkflowRequest
    ) -> analytics_v1_funnel_workflow_service_pb2.InspectFunnelWorkflowResponse:
        """Returns a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_workflow_service_pb2.InspectFunnelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectFunnelWorkflow', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'InspectFunnelWorkflow', {})
            response_0 = ledger_v1_ledger_account_service_pb2.CreateLedgerAccountResponse()
            outgoing_0 = ledger_v1_ledger_account_service_pb2.CreateLedgerAccountRequest(
                context=request.context,
                ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline),
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    external_account_id=request.funnel_id,
                    labels=dict(request.context.baggage)
                )
            )
            response_0 = await deps.clients.ledger_ledger_account.CreateLedgerAccount(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.ledger_account.contact.email
            if returned_0_0:
                response.funnel.owner.email = returned_0_0
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            return response

    async def handle_list_funnel_workflows(
        self,
        request: analytics_v1_funnel_workflow_service_pb2.ListFunnelWorkflowsRequest
    ) -> analytics_v1_funnel_workflow_service_pb2.ListFunnelWorkflowsResponse:
        """Lists funnels a page at a time."""
        deps = self.deps
        response = analytics_v1_funnel_workflow_service_pb2.ListFunnelWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListFunnelWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListFunnelWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = labeling_v1_label_set_approval_service_pb2.ListPendingLabelSetsResponse()
            outgoing_0 = labeling_v1_label_set_approval_service_pb2.ListPendingLabelSetsRequest(
                context=request.context,
                filter=labeling_v1_label_set_approval_service_pb2.ListPendingLabelSetsRequest.Filter(
                    owner_id=request.filter.owner_id
                ),
                page=common_v1_paging_pb2.PageRequest(page_token=request.page.page_token)
            )
            response_0 = await deps.clients.labeling_label_set_approval.ListPendingLabelSets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            return response

    async def handle_resume_funnel_workflow(
        self,
        request: analytics_v1_funnel_workflow_service_pb2.ResumeFunnelWorkflowRequest
    ) -> analytics_v1_funnel_workflow_service_pb2.ResumeFunnelWorkflowResponse:
        """Resumes a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_workflow_service_pb2.ResumeFunnelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeFunnelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ResumeFunnelWorkflow', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = authorization_v1_access_policy_query_service_pb2.ResolveAccessPoliciesResponse()
            response_1 = labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsResponse()
            response_2 = analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowResponse()
            outgoing_0 = authorization_v1_access_policy_query_service_pb2.ResolveAccessPoliciesRequest(
                context=request.context
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                authorization_v1_access_policy_query_service_pb2.ResolveAccessPoliciesRequest()
            )
            response_0 = await deps.clients.authorization_access_policy_query.ResolveAccessPolicies(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.owner_id = request.funnel.owner.user_id
            merged_1 = labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.labeling_annotation_reporting.CountAnnotationTotals(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest(
                context=request.context,
                details=analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        name=request.details.notify.name,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.analytics_analytics_event_workflow.ResumeAnalyticsEventWorkflow(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.details.parameters
            response.funnel.parameters.update(echoed_1)
            return response

    async def handle_retry_funnel_workflow(
        self,
        request: analytics_v1_funnel_workflow_service_pb2.RetryFunnelWorkflowRequest
    ) -> analytics_v1_funnel_workflow_service_pb2.RetryFunnelWorkflowResponse:
        """Retrys a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_workflow_service_pb2.RetryFunnelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryFunnelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RetryFunnelWorkflow', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = yards_v1_yard_query_service_pb2.SummarizeYardsResponse()
            response_1 = customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityResponse()
            response_2 = metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesResponse()
            outgoing_0 = yards_v1_yard_query_service_pb2.SummarizeYardsRequest(
                context=request.context,
                reason=request.funnel.block.reason
            )
            outgoing_1 = customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityRequest(
                context=request.context,
                details=customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                ),
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.funnel.audit.etag),
                    discount=customers_v1_customers_pb2.PreferenceDiscountAction(amount=request.funnel.discount.amount),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.funnel.owner.user_id)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.yards_yard_query.SummarizeYards(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.customers_preference_validation.CheckPreferenceEligibility(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.details.recipient.preferred_channel = request.details.notify.preferred_channel
            outgoing_2.details.recipient.email = response_1.preference.owner.email
            if request.funnel.WhichOneof('action') == 'block':
                outgoing_2.reason = request.funnel.block.reason
            outgoing_2.details.recipient.name.CopyFrom(request.details.notify.name)
            response_2 = await deps.clients.metrics_metric_series_notification.SubscribeMetricSeriesUpdates(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.metric_series.owner.display_name
            if returned_2_1:
                response.funnel.owner.display_name = returned_2_1
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.version
            response.funnel.version = echoed_1
            return response

    async def handle_signal_funnel_workflow(
        self,
        request: analytics_v1_funnel_workflow_service_pb2.SignalFunnelWorkflowRequest
    ) -> analytics_v1_funnel_workflow_service_pb2.SignalFunnelWorkflowResponse:
        """Signals a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_workflow_service_pb2.SignalFunnelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalFunnelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SignalFunnelWorkflow', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowResponse()
            response_1 = analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowResponse()
            outgoing_0 = datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.funnel.owner.email)
                ),
                details=datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowRequest.Details(
                    notify=request.details.notify
                )
            )
            send_0 = partial(
                deps.clients.datasets_dataset_version_workflow.AdvanceDatasetVersionWorkflow,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            outgoing_1 = analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowRequest(
                analytics_event=analytics_v1_analytics_pb2.AnalyticsEvent(
                    subject=analytics_v1_refs_pb2.FunnelRef(
                        funnel_id=request.funnel.funnel_id,
                        version=request.funnel.version
                    )
                ),
                context=request.context,
                details=analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify.email,
                        name=request.details.notify.name
                    )
                )
            )
            response_1 = await hooks.funnel_workflow_signal_funnel_workflow1(
                deps.clients.analytics_analytics_event_workflow,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.name
            response.funnel.name = echoed_1
            return response

    async def handle_start_funnel_workflow(
        self,
        request: analytics_v1_funnel_workflow_service_pb2.StartFunnelWorkflowRequest
    ) -> analytics_v1_funnel_workflow_service_pb2.StartFunnelWorkflowResponse:
        """Starts a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_workflow_service_pb2.StartFunnelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartFunnelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'StartFunnelWorkflow', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = customers_v1_customer_service_pb2.CreateCustomerResponse()
            response_1 = datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowResponse()
            outgoing_0 = customers_v1_customer_service_pb2.CreateCustomerRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.customer.contact.phone = request.details.notify.phone
            outgoing_0.customer.audit.created_by = request.funnel.audit.created_by
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.customers_customer.CreateCustomer(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowRequest(
                context=request.context,
                details=datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify.email,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                )
            )
            port_1: FunnelWorkflowStartFunnelWorkflow1Port = FunnelWorkflowStartFunnelWorkflow1Adapter(
                deps.clients.datasets_dataset_version_workflow,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.customer.relationship_manager.email
            if returned_0_1:
                response.funnel.owner.email = returned_0_1
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.dataset_version.subject.display_name
            if returned_1_1:
                response.funnel.owner.display_name = returned_1_1
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.description
            response.funnel.description = echoed_1
            return response
