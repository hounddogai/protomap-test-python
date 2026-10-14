"""Application workflow for Anomaly ."""

from __future__ import annotations

from typing import Any
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2

from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.domains.anomalies.models import AnomalyUpdateAnomaly1Command
from acme_data.domains.anomalies.models import to_anomaly_update_anomaly1_command
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnomalyServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_batch_create_anomalies(
        self,
        request: anomalies_v1_anomaly_service_pb2.BatchCreateAnomaliesRequest
    ) -> anomalies_v1_anomaly_service_pb2.BatchCreateAnomaliesResponse:
        """Takes a stream of anomalies and answers once at the end."""
        deps = self.deps
        response = anomalies_v1_anomaly_service_pb2.BatchCreateAnomaliesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BatchCreateAnomalies', extra={'fields': {'sequence': request.sequence}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BatchCreateAnomalies',
                {'sequence': request.sequence}
            )
            if request.WhichOneof('chunk') == 'record':
                await deps.repository.save_anomaly(request.context.tenant_id, request.record)
            response_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.ScoreAnomalyFeedbackResponse()
            response_1 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse()
            response_2 = metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersResponse()
            response_3 = lineage_v1_lineage_node_query_service_pb2.BrowseLineageNodesResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.ScoreAnomalyFeedbackRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.record.customer.display_name)
                ),
                context=request.context
            )
            outgoing_1 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.record.assignee.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            outgoing_2 = metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersRequest(
                context=request.context,
                details=metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.record.requester.email,
                        phone=request.header.submitted_by.phone,
                        preferred_channel=request.header.submitted_by.preferred_channel
                    )
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.anomalies_anomaly_feedback_validation.ScoreAnomalyFeedback(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.lineage_lineage_node_calculation.QuoteLineageNode(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.metrics_metric_alert_notification.NotifyMetricAlertWatchers(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_3 = lineage_v1_lineage_node_query_service_pb2.BrowseLineageNodesRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.filter.region = response_1.lineage_node.location.region
            if request.WhichOneof('chunk') == 'record':
                outgoing_3.filter.created_after.CopyFrom(request.record.audit.updated_at)
            response_3 = await deps.clients.lineage_lineage_node_query.BrowseLineageNodes(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.anomaly_feedback.sequence
            returned_0_0_part_0 = response.rejections.add()
            if returned_0_0:
                returned_0_0_part_0.sequence = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            return response

    async def handle_batch_get_anomalies(
        self,
        request: anomalies_v1_anomaly_service_pb2.BatchGetAnomaliesRequest
    ) -> anomalies_v1_anomaly_service_pb2.BatchGetAnomaliesResponse:
        """Returns several anomalies at once."""
        deps = self.deps
        response = anomalies_v1_anomaly_service_pb2.BatchGetAnomaliesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BatchGetAnomalies', extra={'fields': {'domain': 'anomalies'}})
            await deps.repository.audit(request.context.tenant_id, 'BatchGetAnomalies', {})
            response_0 = notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityResponse()
            response_1 = anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksResponse()
            outgoing_0 = notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityRequest(
                context=request.context,
                details=notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.notifications_notification_validation.CheckNotificationEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=response_0.notification.assignee.display_name)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        phone=response_0.notification.requester.phone,
                        preferred_channel=response_0.notification.requester.preferred_channel
                    )
                )
            )
            response_1 = await deps.clients.anomalies_anomaly_feedback_validation.LintAnomalyFeedbacks(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.notification.audit.created_by
            returned_0_0_part_0 = response.anomalies.add()
            if returned_0_0:
                returned_0_0_part_0.audit.created_by = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            return response

    async def handle_create_anomaly(
        self,
        request: anomalies_v1_anomaly_service_pb2.CreateAnomalyRequest
    ) -> anomalies_v1_anomaly_service_pb2.CreateAnomalyResponse:
        """Creates an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_service_pb2.CreateAnomalyResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CreateAnomaly', extra={'fields': {'request_id': request.request_id}})
            await deps.repository.audit(request.context.tenant_id, 'CreateAnomaly', {'request_id': request.request_id})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsResponse()
            response_1 = featureflags_v1_feature_flag_service_pb2.CloneFeatureFlagResponse()
            response_2 = anomalies_v1_anomaly_feedback_validation_service_pb2.CheckAnomalyFeedbackEligibilityResponse()
            outgoing_0 = ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsRequest.Filter(
                    created_after=request.anomaly.audit.created_at
                )
            )
            method_name_0 = 'SuggestLedgerAccounts'
            response_0 = await getattr(
                deps.clients.ledger_ledger_account_query,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'feature_flag': {
                    'audit': {
                        'created_at': request.anomaly.audit.created_at,
                        'etag': request.anomaly.audit.etag,
                        'updated_at': request.anomaly.audit.updated_at
                    },
                    'owner': {'display_name': request.anomaly.assignee.display_name}
                }
            }
            outgoing_1 = featureflags_v1_feature_flag_service_pb2.CloneFeatureFlagRequest(**fields_1)
            response_1 = await deps.clients.featureflags_feature_flag.CloneFeatureFlag(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = anomalies_v1_anomaly_feedback_validation_service_pb2.CheckAnomalyFeedbackEligibilityRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.anomaly.customer.display_name)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_validation_service_pb2.CheckAnomalyFeedbackEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.anomaly.assignee.email,
                        name=request.anomaly.requester.name,
                        preferred_channel=request.anomaly.requester.preferred_channel
                    )
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(
                document_2,
                anomalies_v1_anomaly_feedback_validation_service_pb2.CheckAnomalyFeedbackEligibilityRequest()
            )
            response_2 = await deps.clients.anomalies_anomaly_feedback_validation.CheckAnomalyFeedbackEligibility(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.feature_flag.audit.created_by
            if returned_1_0:
                response.anomaly.audit.created_by = returned_1_0
            returned_1_1 = response_1.feature_flag.owner.email
            if returned_1_1:
                response.anomaly.assignee.email = returned_1_1
            returned_2_0 = response_2.anomaly_feedback.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.anomaly.custom_fields
            response.anomaly.custom_fields.update(echoed_0)
            echoed_1 = request.anomaly.subject
            response.anomaly.subject = echoed_1
            return response

    async def handle_get_anomaly(
        self,
        request: anomalies_v1_anomaly_service_pb2.GetAnomalyRequest
    ) -> anomalies_v1_anomaly_service_pb2.GetAnomalyResponse:
        """Returns an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_service_pb2.GetAnomalyResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetAnomaly', extra={'fields': {'domain': 'anomalies'}})
            await deps.repository.audit(request.context.tenant_id, 'GetAnomaly', {})
            response_0 = lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeResponse()
            outgoing_0 = lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.lineage_lineage_edge_validation.PreviewLineageEdge(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            return response

    async def handle_search_anomalies(
        self,
        request: anomalies_v1_anomaly_service_pb2.SearchAnomaliesRequest
    ) -> anomalies_v1_anomaly_service_pb2.SearchAnomaliesResponse:
        """Lists anomalies a page at a time."""
        deps = self.deps
        response = anomalies_v1_anomaly_service_pb2.SearchAnomaliesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SearchAnomalies', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SearchAnomalies', {'order_by': request.order_by})
            response_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.ValidateAnomalyFeedbackResponse()
            response_1 = anomalies_v1_anomaly_feedback_validation_service_pb2.ScoreAnomalyFeedbackResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.ValidateAnomalyFeedbackRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(source=request.filter.owner_id),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_validation_service_pb2.ValidateAnomalyFeedbackRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.anomalies_anomaly_feedback_validation.ValidateAnomalyFeedback(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_feedback_validation_service_pb2.ScoreAnomalyFeedbackRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    kind=response_0.anomaly_feedback.kind,
                    subject=datasets_v1_refs_pb2.DatasetRef(
                        code=response_0.anomaly_feedback.subject.code,
                        display_name=response_0.anomaly_feedback.subject.display_name
                    )
                ),
                context=request.context
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = anomalies_v1_anomaly_feedback_validation_service_pb2.ScoreAnomalyFeedbackRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.anomalies_anomaly_feedback_validation.ScoreAnomalyFeedback(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.anomaly_feedback.subject.display_name
            returned_1_1_part_0 = response.anomalies.add()
            if returned_1_1:
                returned_1_1_part_0.assignee.display_name = returned_1_1
            return response

    async def handle_update_anomaly(
        self,
        request: anomalies_v1_anomaly_service_pb2.UpdateAnomalyRequest
    ) -> anomalies_v1_anomaly_service_pb2.UpdateAnomalyResponse:
        """Changes an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_service_pb2.UpdateAnomalyResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UpdateAnomaly', extra={'fields': {'allow_missing': request.allow_missing}})
            await deps.repository.audit(
                request.context.tenant_id,
                'UpdateAnomaly',
                {'allow_missing': request.allow_missing}
            )
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse()
            response_1 = anomalies_v1_anomaly_feedback_validation_service_pb2.ValidateAnomalyFeedbackResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.anomaly.WhichOneof('origin') == 'customer':
                outgoing_0.anomaly_feedback.subject.display_name = request.anomaly.customer.display_name
            field_0_2_part_1 = outgoing_0.anomaly_feedback.measurements.add()
            field_0_2_part_1.observed_at.CopyFrom(request.anomaly.audit.created_at)
            outgoing_0.anomaly_feedback.occurred_at.CopyFrom(request.anomaly.sla.due_at)
            outgoing_0.anomaly_feedback.source = request.anomaly.assignee.user_id
            response_0 = await deps.clients.anomalies_anomaly_feedback_calculation.EstimateAnomalyFeedback(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = AnomalyUpdateAnomaly1Command(
                context=request.context,
                anomaly_feedback_subject_display_name=request.anomaly.customer.display_name
            )
            outgoing_1 = to_anomaly_update_anomaly1_command(command_1)
            response_1 = await deps.clients.anomalies_anomaly_feedback_validation.ValidateAnomalyFeedback(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.anomaly_feedback.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            echoed_0 = request.anomaly.requester
            response.anomaly.requester.CopyFrom(echoed_0)
            echoed_1 = request.anomaly.assignee
            response.anomaly.assignee.CopyFrom(echoed_1)
            return response
