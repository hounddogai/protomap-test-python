"""Application workflow for FeatureValue Workflow."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage

from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.anomalies.v1 import detector_approval_service_pb2 as anomalies_v1_detector_approval_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import dataset_version_query_service_pb2 as datasets_v1_dataset_version_query_service_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.featurestore.v1 import entity_validation_service_pb2 as featurestore_v1_entity_validation_service_pb2
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import (
    feature_value_workflow_service_pb2 as featurestore_v1_feature_value_workflow_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_import_service_pb2 as lineage_v1_impact_import_service_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2
from acme.treasury.v1 import cash_position_query_service_pb2 as treasury_v1_cash_position_query_service_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureValueWorkflowAdvanceFeatureValueWorkflow0Command
from acme_data.domains.featurestore.models import FeatureValueWorkflowStartFeatureValueWorkflow1Command
from acme_data.domains.featurestore.models import to_feature_value_workflow_advance_feature_value_workflow0_command
from acme_data.domains.featurestore.models import to_feature_value_workflow_start_feature_value_workflow1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FeatureValueWorkflowServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_advance_feature_value_workflow(
        self,
        request: featurestore_v1_feature_value_workflow_service_pb2.AdvanceFeatureValueWorkflowRequest
    ) -> featurestore_v1_feature_value_workflow_service_pb2.AdvanceFeatureValueWorkflowResponse:
        """Advances a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_workflow_service_pb2.AdvanceFeatureValueWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceFeatureValueWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceFeatureValueWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = anomalies_v1_detector_approval_service_pb2.RecallDetectorResponse()
            response_1 = venues_v1_venue_validation_service_pb2.ScoreVenueResponse()
            command_0 = FeatureValueWorkflowAdvanceFeatureValueWorkflow0Command.model_validate(
                {'context': request.context, 'detector_owner_email': request.details.notify.email}
            )
            outgoing_0 = to_feature_value_workflow_advance_feature_value_workflow0_command(command_0)
            response_0 = await deps.clients.anomalies_detector_approval.RecallDetector(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = venues_v1_venue_validation_service_pb2.ScoreVenueRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    owner=identity_v1_refs_pb2.UserRef(user_id=response_0.detector.owner.user_id)
                )
            )
            send_1 = partial(deps.clients.venues_venue_validation.ScoreVenue, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.kind
            response.feature_value.kind = echoed_1
            return response

    async def handle_cancel_feature_value_workflow(
        self,
        request: featurestore_v1_feature_value_workflow_service_pb2.CancelFeatureValueWorkflowRequest
    ) -> featurestore_v1_feature_value_workflow_service_pb2.CancelFeatureValueWorkflowResponse:
        """Cancels a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_workflow_service_pb2.CancelFeatureValueWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelFeatureValueWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelFeatureValueWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsResponse()
            response_1 = datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaResponse()
            response_2 = treasury_v1_cash_position_query_service_pb2.ExportCashPositionsResponse()
            response_3 = featurestore_v1_entity_validation_service_pb2.PreviewEntityResponse()
            outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                )
            )
            response_0 = await hooks.feature_value_workflow_cancel_feature_value_workflow0(
                deps.clients.lineage_lineage_edge_import,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.data_schema.children.add()
            field_1_1_part_2 = field_1_1_part_1.children.add()
            field_1_1_part_2.manager.display_name = request.feature_value.subject.display_name
            field_1_2_part_1 = outgoing_1.data_schema.children.add()
            field_1_2_part_2 = field_1_2_part_1.children.add()
            field_1_2_part_3 = field_1_2_part_2.children.add()
            field_1_2_part_3.attributes.update(dict(response_0.lineage_edge.attributes))
            field_1_3_part_1 = outgoing_1.data_schema.children.add()
            field_1_3_part_1.manager.email = request.details.notify.email
            outgoing_1.data_schema.manager.display_name = response_0.lineage_edge.subject.display_name
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.datasets_data_schema_calculation.EstimateDataSchema(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = treasury_v1_cash_position_query_service_pb2.ExportCashPositionsRequest(
                context=request.context,
                filter=treasury_v1_cash_position_query_service_pb2.ExportCashPositionsRequest.Filter(
                    region=response_1.data_schema.location.region
                )
            )
            async for chunk_2 in deps.clients.treasury_cash_position_query.ExportCashPositions(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            outgoing_3 = featurestore_v1_entity_validation_service_pb2.PreviewEntityRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                )
            )
            steps_3 = [
                partial(
                    deps.clients.featurestore_entity_validation.PreviewEntity,
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            ]
            results_3 = await run_steps(steps_3)
            response_3 = results_3[-1]
            returned_0_0 = response_0.lineage_edge.sequence
            if returned_0_0:
                response.feature_value.sequence = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            returned_3_1 = response_3.outcome.message
            if returned_3_1:
                response.result.message = returned_3_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.kind
            response.feature_value.kind = echoed_1
            return response

    async def handle_inspect_feature_value_workflow(
        self,
        request: featurestore_v1_feature_value_workflow_service_pb2.InspectFeatureValueWorkflowRequest
    ) -> featurestore_v1_feature_value_workflow_service_pb2.InspectFeatureValueWorkflowResponse:
        """Returns a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_workflow_service_pb2.InspectFeatureValueWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectFeatureValueWorkflow', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'InspectFeatureValueWorkflow', {})
            response_0 = featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewResponse()
            response_1 = featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsResponse()
            outgoing_0 = featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewRequest(
                context=request.context,
                details=featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.featurestore_feature_view_validation.PreviewFeatureView(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.feature_view.WhichOneof('locator') == 'address':
                outgoing_1.filter.region = response_0.feature_view.address.region
            outgoing_1.filter.created_after.CopyFrom(response_0.feature_view.audit.updated_at)
            outgoing_1.filter.labels.update(dict(response_0.result.details))
            outgoing_1.filter.owner_id = response_0.feature_view.owner.user_id
            response_1 = await deps.clients.featurestore_entity_reporting.CountEntityTotals(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.feature_view.code
            if returned_0_1:
                response.feature_value.subject.code = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            return response

    async def handle_list_feature_value_workflows(
        self,
        request: featurestore_v1_feature_value_workflow_service_pb2.ListFeatureValueWorkflowsRequest
    ) -> featurestore_v1_feature_value_workflow_service_pb2.ListFeatureValueWorkflowsResponse:
        """Lists feature values a page at a time."""
        deps = self.deps
        response = featurestore_v1_feature_value_workflow_service_pb2.ListFeatureValueWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListFeatureValueWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListFeatureValueWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = venues_v1_venue_validation_service_pb2.ScoreVenueResponse()
            outgoing_0 = venues_v1_venue_validation_service_pb2.ScoreVenueRequest(
                context=request.context,
                details=venues_v1_venue_validation_service_pb2.ScoreVenueRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                venue=venues_v1_venues_pb2.Venue(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.venues_venue_validation.ScoreVenue(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_resume_feature_value_workflow(
        self,
        request: featurestore_v1_feature_value_workflow_service_pb2.ResumeFeatureValueWorkflowRequest
    ) -> featurestore_v1_feature_value_workflow_service_pb2.ResumeFeatureValueWorkflowResponse:
        """Resumes a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_workflow_service_pb2.ResumeFeatureValueWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeFeatureValueWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeFeatureValueWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = lineage_v1_impact_import_service_pb2.MapImpactImportColumnsResponse()
            outgoing_0 = lineage_v1_impact_import_service_pb2.MapImpactImportColumnsRequest(
                context=request.context,
                details=lineage_v1_impact_import_service_pb2.MapImpactImportColumnsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.notify.email),
                    requester=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                )
            )
            method_name_0 = 'MapImpactImportColumns'
            response_0 = await getattr(
                deps.clients.lineage_impact_import,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.impact.customer.display_name
            if returned_0_0:
                response.feature_value.subject.display_name = returned_0_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_retry_feature_value_workflow(
        self,
        request: featurestore_v1_feature_value_workflow_service_pb2.RetryFeatureValueWorkflowRequest
    ) -> featurestore_v1_feature_value_workflow_service_pb2.RetryFeatureValueWorkflowResponse:
        """Retrys a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_workflow_service_pb2.RetryFeatureValueWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryFeatureValueWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryFeatureValueWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesResponse()
            response_1 = metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesResponse()
            outgoing_0 = lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesRequest.Filter(
                    created_after=request.feature_value.occurred_at,
                    labels=dict(request.feature_value.attributes)
                )
            )
            outgoing_1 = metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesRequest(
                context=request.context,
                details=metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify.email,
                        phone=request.details.notify.phone
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.lineage_lineage_node_approval.ListPendingLineageNodes(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.metrics_dashboard_notification.SubscribeDashboardUpdates(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.attributes
            response.feature_value.attributes.update(echoed_1)
            return response

    async def handle_signal_feature_value_workflow(
        self,
        request: featurestore_v1_feature_value_workflow_service_pb2.SignalFeatureValueWorkflowRequest
    ) -> featurestore_v1_feature_value_workflow_service_pb2.SignalFeatureValueWorkflowResponse:
        """Signals a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_workflow_service_pb2.SignalFeatureValueWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalFeatureValueWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalFeatureValueWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = search_v1_search_index_validation_service_pb2.ScoreSearchIndexResponse()
            response_1 = lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowResponse()
            response_2 = lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowResponse()
            callbacks_0: list[
                Callable[[], Awaitable[search_v1_search_index_validation_service_pb2.ScoreSearchIndexResponse]]
            ] = []
            for item_0 in request.feature_value.measurements:
                outgoing_0 = search_v1_search_index_validation_service_pb2.ScoreSearchIndexRequest(
                    context=request.context,
                    search_index=search_v1_search_pb2.SearchIndex(
                        dimensions=search_v1_search_pb2.SearchIndexDimensions(unit=item_0.unit),
                        owner=identity_v1_refs_pb2.UserRef(display_name=request.feature_value.subject.display_name)
                    )
                )
                async def send_0(
                    payload: search_v1_search_index_validation_service_pb2.ScoreSearchIndexRequest = outgoing_0
                ) -> search_v1_search_index_validation_service_pb2.ScoreSearchIndexResponse:
                    return await deps.clients.search_search_index_validation.ScoreSearchIndex(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            outgoing_1 = lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.lineage_edge.subject.display_name = request.feature_value.subject.display_name
            outgoing_1.details.notify.email = response_0.search_index.owner.email
            merged_1 = lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.lineage_lineage_edge_workflow.CancelLineageEdgeWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=response_1.lineage_edge.subject.display_name),
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=response_0.search_index.audit.created_at,
                        created_by=response_0.search_index.audit.created_by
                    ),
                    customer=customers_v1_refs_pb2.CustomerRef(display_name=request.feature_value.subject.display_name)
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.lineage_impact_workflow.SignalImpactWorkflow(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.lineage_edge.source
            if returned_1_1:
                response.feature_value.source = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_start_feature_value_workflow(
        self,
        request: featurestore_v1_feature_value_workflow_service_pb2.StartFeatureValueWorkflowRequest
    ) -> featurestore_v1_feature_value_workflow_service_pb2.StartFeatureValueWorkflowResponse:
        """Starts a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_workflow_service_pb2.StartFeatureValueWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartFeatureValueWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartFeatureValueWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_feature_value_sync_service_pb2.SyncFeatureValuesResponse()
            response_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackResponse()
            response_2 = datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsResponse()
            async for item_0 in async_messages(request.feature_value.measurements):
                outgoing_0 = featurestore_v1_feature_value_sync_service_pb2.SyncFeatureValuesRequest(
                    context=request.context,
                    feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                        measurements=[
                            featurestore_v1_featurestore_pb2.FeatureValueMeasurement(observed_at=item_0.observed_at)
                        ]
                    )
                )
                response_0 = await deps.clients.featurestore_feature_value_sync.SyncFeatureValues(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            command_1 = FeatureValueWorkflowStartFeatureValueWorkflow1Command(
                context=request.context,
                anomaly_feedback_subject_code=response_0.feature_value.subject.code,
                details_effective_at=response_0.outcome.effective_at
            )
            outgoing_1 = to_feature_value_workflow_start_feature_value_workflow1_command(command_1)
            response_1 = await deps.clients.anomalies_anomaly_feedback_approval.SubmitAnomalyFeedback(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            for item_2 in request.feature_value.measurements:
                outgoing_2 = datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest(
                    context=request.context,
                    filter=datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest.Filter(
                        created_after=item_2.observed_at
                    )
                )
                response_2 = await deps.clients.datasets_dataset_version_query.SuggestDatasetVersions(
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            returned_1_0 = response_1.outcome.effective_at
            if returned_1_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_1_0)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.occurred_at
            response.feature_value.occurred_at.CopyFrom(echoed_1)
            return response
