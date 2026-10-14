"""Application workflow for FeatureView Reporting."""

from __future__ import annotations

from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.dispatch.v1 import dispatch_order_service_pb2 as dispatch_v1_dispatch_order_service_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2 as featurestore_v1_feature_view_reporting_service_pb2,
)
from acme.featurestore.v1 import feature_view_service_pb2 as featurestore_v1_feature_view_service_pb2
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.surveys.v1 import survey_service_pb2 as surveys_v1_survey_service_pb2
from acme.surveys.v1 import survey_service_pb2_grpc as surveys_v1_survey_service_pb2_grpc
from acme.surveys.v1 import surveys_pb2 as surveys_v1_surveys_pb2

from acme_data.domains.featurestore.adapters import FeatureViewReportingScheduleFeatureViewReport1Adapter
from acme_data.domains.featurestore.adapters import FeatureViewReportingScheduleFeatureViewReport1Port
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureViewReportingFetchFeatureViewReport1Command
from acme_data.domains.featurestore.models import to_feature_view_reporting_fetch_feature_view_report1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FeatureViewReportingServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_count_feature_view_totals(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.CountFeatureViewTotalsRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.CountFeatureViewTotalsResponse:
        """Counts feature views by status."""
        deps = self.deps
        response = featurestore_v1_feature_view_reporting_service_pb2.CountFeatureViewTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountFeatureViewTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountFeatureViewTotals',
                {'order_by': request.order_by}
            )
            response_0 = datasets_v1_dataset_service_pb2.ListDatasetsResponse()
            outgoing_0 = datasets_v1_dataset_service_pb2.ListDatasetsRequest(
                context=request.context,
                filter=datasets_v1_dataset_service_pb2.ListDatasetsRequest.Filter(
                    created_after=request.filter.created_after,
                    owner_id=request.filter.owner_id
                )
            )
            response_0 = await deps.clients.datasets_dataset.ListDatasets(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            return response

    async def handle_delete_feature_view_report(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.DeleteFeatureViewReportRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.DeleteFeatureViewReportResponse:
        """Deletes a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_reporting_service_pb2.DeleteFeatureViewReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteFeatureViewReport', extra={'fields': {'feature_view_id': request.feature_view_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DeleteFeatureViewReport',
                {'feature_view_id': request.feature_view_id}
            )
            response_0 = surveys_v1_survey_service_pb2.CreateSurveyResponse()
            outgoing_0 = surveys_v1_survey_service_pb2.CreateSurveyRequest(
                context=request.context,
                survey=surveys_v1_surveys_pb2.Survey(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline, etag=request.etag),
                    metadata=dict(request.context.baggage)
                )
            )
            registered_0 = cast(
                surveys_v1_survey_service_pb2_grpc.SurveyServiceStub,
                deps.clients.registry['acme.surveys.v1.SurveyService']
            )
            response_0 = await registered_0.CreateSurvey(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            return response

    async def handle_fetch_feature_view_report(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.FetchFeatureViewReportRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.FetchFeatureViewReportResponse:
        """Returns a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_reporting_service_pb2.FetchFeatureViewReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchFeatureViewReport', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'FetchFeatureViewReport', {})
            response_0 = featurestore_v1_feature_view_validation_service_pb2.GetFeatureViewRulesResponse()
            response_1 = featurestore_v1_entity_calculation_service_pb2.EstimateEntityResponse()
            outgoing_0 = featurestore_v1_feature_view_validation_service_pb2.GetFeatureViewRulesRequest(
                context=request.context,
                feature_view_id=request.feature_view_id
            )
            response_0 = await deps.clients.featurestore_feature_view_validation.GetFeatureViewRules(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = FeatureViewReportingFetchFeatureViewReport1Command.model_validate(
                {'context': request.context, 'entity_contact_email': response_0.feature_view.owner.email}
            )
            outgoing_1 = to_feature_view_reporting_fetch_feature_view_report1_command(command_1)
            response_1 = await deps.clients.featurestore_entity_calculation.EstimateEntity(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.entity.contact.email
            if returned_1_0:
                response.feature_view.owner.email = returned_1_0
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            return response

    async def handle_generate_feature_view_report(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportResponse:
        """Generates a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateFeatureViewReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateFeatureViewReport',
                {'reason': request.reason}
            )
            response_0 = featurestore_v1_feature_view_service_pb2.ListFeatureViewsResponse()
            response_1 = datasets_v1_dataset_query_service_pb2.CountDatasetsResponse()
            outgoing_0 = featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest(
                context=request.context,
                filter=featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest.Filter(
                    labels=dict(request.details.filters),
                    owner_id=request.feature_view_id
                )
            )
            outgoing_1 = datasets_v1_dataset_query_service_pb2.CountDatasetsRequest(
                context=request.context,
                filter=datasets_v1_dataset_query_service_pb2.CountDatasetsRequest.Filter(
                    labels=dict(request.details.filters)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.featurestore_feature_view.ListFeatureViews(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.datasets_dataset_query.CountDatasets(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_feature_view_reports(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsResponse:
        """Lists feature views a page at a time."""
        deps = self.deps
        response = featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListFeatureViewReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListFeatureViewReports',
                {'order_by': request.order_by}
            )
            return response

    async def handle_schedule_feature_view_report(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportResponse:
        """Schedules a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleFeatureViewReport', extra={'fields': {'cron': request.details.cron}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleFeatureViewReport',
                {'cron': request.details.cron}
            )
            response_0 = featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse()
            response_1 = featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse()
            response_2 = metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictResponse()
            response_3 = datasets_v1_dataset_query_service_pb2.SuggestDatasetsResponse()
            outgoing_0 = featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.feature_view.feature_view_id = request.feature_view_id
            outgoing_0.reason = request.reason
            outgoing_0.feature_view.owner.user_id = request.context.actor.user_id
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.featurestore_feature_view_sync.ReconcileFeatureViews(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest(
                context=request.context,
                details=featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        postal_code=response_0.feature_view.address.postal_code
                    )
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=response_0.feature_view.audit.created_by,
                        updated_by=response_0.feature_view.audit.updated_by
                    ),
                    dimensions=featurestore_v1_featurestore_pb2.FeatureViewDimensions(
                        weight=response_0.feature_view.dimensions.weight
                    )
                )
            )
            port_1: FeatureViewReportingScheduleFeatureViewReport1Port = FeatureViewReportingScheduleFeatureViewReport1Adapter(
                deps.clients.featurestore_feature_view_validation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_1.feature_view.audit.created_by),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.feature_view.address.country_code,
                        postal_code=response_1.feature_view.address.postal_code,
                        recipient=response_1.feature_view.address.recipient
                    )
                )
            )
            steps_2 = [
                partial(
                    deps.clients.metrics_dashboard_sync.ResolveDashboardConflict,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            outgoing_3 = datasets_v1_dataset_query_service_pb2.SuggestDatasetsRequest()
            outgoing_3.context.CopyFrom(request.context)
            if response_0.feature_view.WhichOneof('locator') == 'address':
                outgoing_3.filter.region = response_0.feature_view.address.region
            outgoing_3.filter.created_after.CopyFrom(response_2.dashboard.issued_at)
            outgoing_3.filter.owner_id = response_1.feature_view.owner.user_id
            outgoing_3.filter.labels.update(dict(response_2.dashboard.metadata))
            response_3 = await deps.clients.datasets_dataset_query.SuggestDatasets(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.outcome.message
            if returned_2_1:
                response.result.message = returned_2_1
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_feature_view_report(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.ShareFeatureViewReportRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.ShareFeatureViewReportResponse:
        """Shares a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_reporting_service_pb2.ShareFeatureViewReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareFeatureViewReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ShareFeatureViewReport', {'reason': request.reason})
            response_0 = featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse()
            response_1 = featurestore_v1_feature_view_service_pb2.CreateFeatureViewResponse()
            outgoing_0 = featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    feature_view_id=request.feature_view_id,
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.recipient.email)
                )
            )
            response_0 = cast(featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse, await deps.bus.request(
                'acme.featurestore.v1.FeatureViewReportingService/ShareFeatureViewReport/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = featurestore_v1_feature_view_service_pb2.CreateFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=response_0.feature_view.audit.created_at,
                        etag=response_0.feature_view.audit.etag,
                        updated_at=response_0.feature_view.audit.updated_at
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.feature_view.owner.display_name)
                )
            )
            response_1 = await deps.clients.featurestore_feature_view.CreateFeatureView(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.feature_view.audit.created_by
            if returned_0_0:
                response.feature_view.audit.created_by = returned_0_0
            returned_1_0 = response_1.feature_view.dimensions.length
            if returned_1_0:
                response.feature_view.dimensions.length = returned_1_0
            returned_1_1 = response_1.feature_view.dimensions.weight
            if returned_1_1:
                response.feature_view.dimensions.weight = returned_1_1
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.feature_view.owner.email = echoed_1
            return response

    async def handle_stream_feature_view_metrics(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.StreamFeatureViewMetricsRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.StreamFeatureViewMetricsResponse:
        """Streams the changes of feature views as they happen."""
        deps = self.deps
        response = featurestore_v1_feature_view_reporting_service_pb2.StreamFeatureViewMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamFeatureViewMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamFeatureViewMetrics',
                {'max_events': request.max_events}
            )
            response_0 = dispatch_v1_dispatch_order_service_pb2.WatchDispatchOrdersResponse()
            response_1 = datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionResponse()
            response_2 = authorization_v1_access_policy_service_pb2.CreateAccessPolicyResponse()
            outgoing_0 = dispatch_v1_dispatch_order_service_pb2.WatchDispatchOrdersRequest(
                context=request.context,
                filter=dispatch_v1_dispatch_order_service_pb2.WatchDispatchOrdersRequest.Filter(
                    created_after=request.filter.created_after,
                    region=request.filter.region
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.subscriber.email,
                    preferred_channel=request.subscriber.preferred_channel
                )
            )
            async for chunk_0 in deps.clients.dispatch_dispatch_order.WatchDispatchOrders(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            fields_1: dict[str, Any] = {
                'context': request.context,
                'dataset_version': {
                    'attributes': dict(request.filter.labels),
                    'measurements': [{'observed_at': request.filter.created_after}],
                    'subject': {'email': request.subscriber.email}
                },
                'details': {'destination': {'region': request.filter.region}}
            }
            outgoing_1 = datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionRequest(**fields_1)
            response_1 = await deps.clients.datasets_dataset_version_calculation.SimulateDatasetVersion(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = authorization_v1_access_policy_service_pb2.CreateAccessPolicyRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    block=authorization_v1_authorization_pb2.AccessPolicyBlockAction(
                        notify_email=request.subscriber.email
                    ),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=response_1.dataset_version.subject.display_name,
                        email=response_1.dataset_version.subject.email
                    )
                ),
                context=request.context
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(document_2, authorization_v1_access_policy_service_pb2.CreateAccessPolicyRequest())
            response_2 = await deps.clients.authorization_access_policy.CreateAccessPolicy(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.access_policy.description
            if returned_2_0:
                response.feature_view.components['primary'].description = returned_2_0
            echoed_0 = request.subscriber.email
            response.feature_view.owner.email = echoed_0
            return response
