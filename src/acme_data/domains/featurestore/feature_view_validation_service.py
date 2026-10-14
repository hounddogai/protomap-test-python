"""Checks feature views against the rules before anything acts on them."""

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

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.documents.v1 import documents_pb2 as documents_v1_documents_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.maintenance.v1 import work_order_query_service_pb2 as maintenance_v1_work_order_query_service_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import FeatureViewValidationValidateFeatureView2Adapter
from acme_data.domains.featurestore.adapters import FeatureViewValidationValidateFeatureView2Port
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureViewValidationScoreFeatureView1Command
from acme_data.domains.featurestore.models import FeatureViewValidationScoreFeatureView2Command
from acme_data.domains.featurestore.models import to_feature_view_validation_score_feature_view1_command
from acme_data.domains.featurestore.models import to_feature_view_validation_score_feature_view2_command
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class FeatureViewValidationServicer(
    featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def CheckFeatureViewEligibility(
        self, request: featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityResponse:
        """Checks a feature view."""
        return await self.handle_check_feature_view_eligibility(request)

    @rpc_errors
    async def ExplainFeatureViewDecision(
        self, request: featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionResponse:
        """Explains a feature view."""
        return await self.handle_explain_feature_view_decision(request)

    @rpc_errors
    @retry_transient
    async def GetFeatureViewRules(
        self, request: featurestore_v1_feature_view_validation_service_pb2.GetFeatureViewRulesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_validation_service_pb2.GetFeatureViewRulesResponse:
        """Returns a feature view."""
        return await self.handle_get_feature_view_rules(request)

    @rpc_errors
    async def PreviewFeatureView(
        self, request: featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewResponse:
        """Previews a feature view."""
        return await self.handle_preview_feature_view(request)

    @rpc_errors
    async def ScoreFeatureView(
        self, request: featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse:
        """Scores a feature view."""
        return await self.handle_score_feature_view(request)

    @rpc_errors
    async def ValidateFeatureView(
        self, request: featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewResponse:
        """Validates a feature view."""
        return await self.handle_validate_feature_view(request)

    async def handle_check_feature_view_eligibility(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityResponse:
        """Checks a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckFeatureViewEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckFeatureViewEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = metrics_v1_dashboard_notification_service_pb2.NotifyDashboardWatchersResponse()
            response_1 = featurestore_v1_feature_view_calculation_service_pb2.GetFeatureViewRatesResponse()
            outgoing_0 = metrics_v1_dashboard_notification_service_pb2.NotifyDashboardWatchersRequest(
                context=request.context,
                details=metrics_v1_dashboard_notification_service_pb2.NotifyDashboardWatchersRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.feature_view.owner.email,
                        name=request.details.contact.name,
                        phone=request.details.contact.phone,
                        preferred_channel=request.details.contact.preferred_channel
                    )
                )
            )
            outgoing_1 = featurestore_v1_feature_view_calculation_service_pb2.GetFeatureViewRatesRequest(
                context=request.context,
                feature_view_id=request.feature_view_id
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.metrics_dashboard_notification.NotifyDashboardWatchers(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_feature_view_calculation.GetFeatureViewRates(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.feature_view.owner.email
            if returned_1_0:
                response.feature_view.owner.email = returned_1_0
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.code
            response.feature_view.code = echoed_1
            return response

    async def handle_explain_feature_view_decision(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionResponse:
        """Explains a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainFeatureViewDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainFeatureViewDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = metrics_v1_dashboard_sync_service_pb2.ReconcileDashboardsResponse()
            response_1 = anomalies_v1_detector_validation_service_pb2.PreviewDetectorResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'dashboard': {
                    'audit': {'updated_by': request.feature_view.audit.updated_by},
                    'billing_address': {
                        'locality': request.feature_view.address.locality,
                        'recipient': request.feature_view.address.recipient
                    }
                }
            }
            outgoing_0 = metrics_v1_dashboard_sync_service_pb2.ReconcileDashboardsRequest(**fields_0)
            response_0 = await deps.clients.metrics_dashboard_sync.ReconcileDashboards(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_detector_validation_service_pb2.PreviewDetectorRequest(
                context=request.context,
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.dashboard.counterparty.display_name)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, anomalies_v1_detector_validation_service_pb2.PreviewDetectorRequest())
            response_1 = await deps.clients.anomalies_detector_validation.PreviewDetector(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.audit.created_by
            if returned_0_0:
                response.feature_view.audit.created_by = returned_0_0
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.code
            response.feature_view.code = echoed_1
            return response

    async def handle_get_feature_view_rules(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.GetFeatureViewRulesRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.GetFeatureViewRulesResponse:
        """Returns a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_validation_service_pb2.GetFeatureViewRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFeatureViewRules', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetFeatureViewRules',
                {'locale': request.context.locale}
            )
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            return response

    async def handle_preview_feature_view(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewResponse:
        """Previews a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewFeatureView', {'reason': request.reason})
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorResponse()
            response_1 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse()
            response_2 = featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueResponse()
            outgoing_0 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest(
                context=request.context,
                details=anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
                )
            )
            outgoing_1 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.feature_view.address.country_code,
                        lines=list(request.feature_view.address.lines),
                        postal_code=request.feature_view.address.postal_code,
                        recipient=request.feature_view.address.recipient
                    )
                )
            )
            outgoing_2 = featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(locality=request.feature_view.address.locality)
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.anomalies_detector_validation.NormalizeDetector(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.featurestore_feature_value_calculation.RecalculateFeatureValues(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_feature_value_calculation.SimulateFeatureValue(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.outcome.reference_id
            if returned_0_0:
                response.outcome.reference_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.specs
            response.feature_view.specs.update(echoed_1)
            return response

    async def handle_score_feature_view(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse:
        """Scores a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreFeatureView', extra={'fields': {'currency_code': request.details.currency_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScoreFeatureView',
                {'currency_code': request.details.currency_code}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsResponse()
            response_1 = notifications_v1_notification_service_pb2.SearchNotificationsResponse()
            response_2 = notifications_v1_notification_service_pb2.ListNotificationsResponse()
            response_3 = maintenance_v1_work_order_query_service_pb2.SummarizeWorkOrdersResponse()
            outgoing_0 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest.Filter(
                    created_after=request.feature_view.audit.updated_at,
                    region=request.feature_view.address.region
                )
            )
            registered_0 = cast(
                ledger_v1_ledger_account_service_pb2_grpc.LedgerAccountServiceStub,
                deps.clients.registry['acme.ledger.v1.LedgerAccountService']
            )
            response_0 = await registered_0.SearchLedgerAccounts(outgoing_0, timeout=deps.settings.timeout)
            command_1 = FeatureViewValidationScoreFeatureView1Command(
                context=request.context,
                filter_region=request.details.destination.region
            )
            outgoing_1 = to_feature_view_validation_score_feature_view1_command(command_1)
            response_1 = await deps.clients.notifications_notification.SearchNotifications(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            command_2 = FeatureViewValidationScoreFeatureView2Command.model_validate(
                {'context': request.context, 'filter_region': request.details.destination.region}
            )
            outgoing_2 = to_feature_view_validation_score_feature_view2_command(command_2)
            response_2 = await deps.clients.notifications_notification.ListNotifications(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = maintenance_v1_work_order_query_service_pb2.SummarizeWorkOrdersRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=maintenance_v1_work_order_query_service_pb2.SummarizeWorkOrdersRequest.Details(
                    filters=dict(response_0.result.details)
                ),
                reason=request.reason
            )
            send_3 = partial(
                deps.clients.maintenance_work_order_query.SummarizeWorkOrders,
                timeout=deps.settings.timeout
            )
            response_3 = await send_3(outgoing_3)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.name
            response.feature_view.name = echoed_1
            return response

    async def handle_validate_feature_view(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewResponse:
        """Validates a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateFeatureView', {'reason': request.reason})
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueResponse()
            response_1 = lineage_v1_impact_calculation_service_pb2.RecalculateImpactsResponse()
            response_2 = documents_v1_document_validation_service_pb2.ValidateDocumentResponse()
            outgoing_0 = featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.feature_view.address.country_code
                    )
                )
            )
            response_0 = await hooks.feature_view_validation_validate_feature_view0(
                deps.clients.featurestore_feature_value_calculation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = lineage_v1_impact_calculation_service_pb2.RecalculateImpactsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.impact.customer.display_name = response_0.feature_value.subject.display_name
            outgoing_1.impact.requester.email = request.feature_view.owner.email
            outgoing_1.impact.requester.preferred_channel = request.details.contact.preferred_channel
            outgoing_1.impact.assignee.email = request.details.contact.email
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.lineage_impact_calculation.RecalculateImpacts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = documents_v1_document_validation_service_pb2.ValidateDocumentRequest(
                context=request.context,
                document=documents_v1_documents_pb2.Document(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        recipient=request.feature_view.address.recipient
                    )
                )
            )
            port_2: FeatureViewValidationValidateFeatureView2Port = FeatureViewValidationValidateFeatureView2Adapter(
                deps.clients.documents_document_validation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.impact.customer.email
            if returned_1_0:
                response.feature_view.owner.email = returned_1_0
            returned_2_0 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_0)
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.capacity
            response.feature_view.capacity = echoed_1
            return response
