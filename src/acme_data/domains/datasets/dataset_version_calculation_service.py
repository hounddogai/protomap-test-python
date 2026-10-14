"""Computes the figures of a dataset version, such as totals, taxes, and estimates."""

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

import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.boxoffice.v1 import box_office_sale_service_pb2 as boxoffice_v1_box_office_sale_service_pb2
from acme.boxoffice.v1 import boxoffice_pb2 as boxoffice_v1_boxoffice_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2_grpc as datasets_v1_dataset_version_calculation_service_pb2_grpc,
)
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.drivers.v1 import driver_query_service_pb2 as drivers_v1_driver_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.labeling.v1 import (
    labeling_task_validation_service_pb2_grpc as labeling_v1_labeling_task_validation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.tours.v1 import tour_service_pb2 as tours_v1_tour_service_pb2
from acme.tours.v1 import tours_pb2 as tours_v1_tours_pb2

from acme_data.domains.datasets import hooks
from acme_data.domains.datasets.adapters import DatasetVersionCalculationCalculateDatasetVersion1Adapter
from acme_data.domains.datasets.adapters import DatasetVersionCalculationCalculateDatasetVersion1Port
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.domains.datasets.models import DatasetVersionCalculationQuoteDatasetVersion2Command
from acme_data.domains.datasets.models import DatasetVersionCalculationSimulateDatasetVersion0Command
from acme_data.domains.datasets.models import to_dataset_version_calculation_quote_dataset_version2_command
from acme_data.domains.datasets.models import to_dataset_version_calculation_simulate_dataset_version0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class DatasetVersionCalculationServicer(
    datasets_v1_dataset_version_calculation_service_pb2_grpc.DatasetVersionCalculationServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def CalculateDatasetVersion(
        self, request: datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse:
        """Calculates a dataset version."""
        return await self.handle_calculate_dataset_version(request)

    @rpc_errors
    async def CompareDatasetVersionOptions(
        self, request: datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse:
        """Compares a dataset version."""
        return await self.handle_compare_dataset_version_options(request)

    @rpc_errors
    async def EstimateDatasetVersion(
        self, request: datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionResponse:
        """Estimates a dataset version."""
        return await self.handle_estimate_dataset_version(request)

    @rpc_errors
    async def ExplainDatasetVersionCalculation(
        self, request: datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationResponse:
        """Explains a dataset version."""
        return await self.handle_explain_dataset_version_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetDatasetVersionRates(
        self, request: datasets_v1_dataset_version_calculation_service_pb2.GetDatasetVersionRatesRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_calculation_service_pb2.GetDatasetVersionRatesResponse:
        """Returns a dataset version."""
        return await self.handle_get_dataset_version_rates(request)

    @rpc_errors
    async def QuoteDatasetVersion(
        self, request: datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionResponse:
        """Quotes a dataset version."""
        return await self.handle_quote_dataset_version(request)

    @rpc_errors
    async def SimulateDatasetVersion(
        self, request: datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionResponse:
        """Simulates a dataset version."""
        return await self.handle_simulate_dataset_version(request)

    async def handle_calculate_dataset_version(
        self,
        request: datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest
    ) -> datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse:
        """Calculates a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateDatasetVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CalculateDatasetVersion',
                {'reason': request.reason}
            )
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = notifications_v1_notification_query_service_pb2.BrowseNotificationsResponse()
            response_1 = featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.BrowseNotificationsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.region = request.details.destination.region
            outgoing_0.filter.created_after.CopyFrom(request.dataset_version.occurred_at)
            outgoing_0.filter.labels.update(dict(request.dataset_version.attributes))
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.notifications_notification_query.BrowseNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewRequest(
                context=request.context,
                details=featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(lines=list(request.details.destination.lines))
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    owner=identity_v1_refs_pb2.UserRef(email=request.dataset_version.subject.email)
                )
            )
            port_1: DatasetVersionCalculationCalculateDatasetVersion1Port = DatasetVersionCalculationCalculateDatasetVersion1Adapter(
                deps.clients.featurestore_feature_view_calculation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.correlation_id
            response.dataset_version.correlation_id = echoed_1
            return response

    async def handle_compare_dataset_version_options(
        self,
        request: datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest
    ) -> datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse:
        """Compares a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareDatasetVersionOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareDatasetVersionOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = documents_v1_document_query_service_pb2.ResolveDocumentsResponse()
            response_1 = boxoffice_v1_box_office_sale_service_pb2.CloneBoxOfficeSaleResponse()
            outgoing_0 = documents_v1_document_query_service_pb2.ResolveDocumentsRequest(context=request.context)
            outgoing_1 = boxoffice_v1_box_office_sale_service_pb2.CloneBoxOfficeSaleRequest(
                box_office_sale=boxoffice_v1_boxoffice_pb2.BoxOfficeSale(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        recipient=request.details.destination.recipient,
                        region=request.details.destination.region
                    )
                ),
                context=request.context
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.documents_document_query.ResolveDocuments(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.boxoffice_box_office_sale.CloneBoxOfficeSale(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.occurred_at
            response.dataset_version.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_estimate_dataset_version(
        self,
        request: datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest
    ) -> datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionResponse:
        """Estimates a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateDatasetVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateDatasetVersion', {'reason': request.reason})
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = notifications_v1_notification_query_service_pb2.ResolveNotificationsResponse()
            response_1 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorResponse()
            response_2 = tours_v1_tour_service_pb2.CreateTourResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.ResolveNotificationsRequest(
                context=request.context
            )
            response_0 = cast(notifications_v1_notification_query_service_pb2.ResolveNotificationsResponse, await deps.bus.request(
                'acme.datasets.v1.DatasetVersionCalculationService/EstimateDatasetVersion/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest(
                context=request.context,
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.dataset_version.subject.display_name,
                        email=request.dataset_version.subject.email
                    )
                )
            )
            response_1 = await deps.clients.anomalies_detector_validation.NormalizeDetector(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = tours_v1_tour_service_pb2.CreateTourRequest(
                context=request.context,
                tour=tours_v1_tours_pb2.Tour(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_1.detector.audit.etag),
                    participants=[
                        tours_v1_tours_pb2.TourParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.dataset_version.subject.email)
                        )
                    ]
                )
            )
            method_name_2 = 'CreateTour'
            response_2 = await getattr(deps.clients.tours_tour, method_name_2)(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.source
            response.dataset_version.source = echoed_1
            return response

    async def handle_explain_dataset_version_calculation(
        self,
        request: datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest
    ) -> datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationResponse:
        """Explains a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainDatasetVersionCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainDatasetVersionCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportResponse()
            response_1 = labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'metric_alert': {'owner': {'display_name': request.dataset_version.subject.display_name}}
            }
            outgoing_0 = metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportRequest(**fields_0)
            response_0 = await deps.clients.metrics_metric_alert_export.RetryMetricAlertExport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            for item_1 in request.dataset_version.measurements:
                outgoing_1 = labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityRequest(
                    context=request.context,
                    labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                        assignee=identity_v1_refs_pb2.UserRef(display_name=response_0.metric_alert.owner.display_name),
                        audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.metric_alert.audit.created_by),
                        comments=[labeling_v1_labeling_pb2.LabelingTaskComment(created_at=item_1.observed_at)],
                        requester=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
                    )
                )
                response_1 = await deps.clients.labeling_labeling_task_validation.CheckLabelingTaskEligibility(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.source
            response.dataset_version.source = echoed_1
            return response

    async def handle_get_dataset_version_rates(
        self,
        request: datasets_v1_dataset_version_calculation_service_pb2.GetDatasetVersionRatesRequest
    ) -> datasets_v1_dataset_version_calculation_service_pb2.GetDatasetVersionRatesResponse:
        """Returns a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_calculation_service_pb2.GetDatasetVersionRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDatasetVersionRates', extra={'fields': {'domain': 'datasets'}})
            await deps.repository.audit(request.context.tenant_id, 'GetDatasetVersionRates', {})
            response_0 = notifications_v1_notification_query_service_pb2.FindNotificationsResponse()
            response_1 = drivers_v1_driver_query_service_pb2.CountDriversResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.FindNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_query_service_pb2.FindNotificationsRequest.Filter(
                    owner_id=request.dataset_version_id
                )
            )
            response_0 = await deps.clients.notifications_notification_query.FindNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = drivers_v1_driver_query_service_pb2.CountDriversRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.labels.update(dict(response_0.result.details))
            outgoing_1.filter.created_after.CopyFrom(request.context.deadline)
            outgoing_1.filter.owner_id = response_0.result.correlation_id
            merged_1 = drivers_v1_driver_query_service_pb2.CountDriversRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.drivers_driver_query.CountDrivers(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            return response

    async def handle_quote_dataset_version(
        self,
        request: datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest
    ) -> datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionResponse:
        """Quotes a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteDatasetVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteDatasetVersion', {'reason': request.reason})
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = notifications_v1_notification_query_service_pb2.FindNotificationsResponse()
            response_1 = labeling_v1_labeling_task_validation_service_pb2.LintLabelingTasksResponse()
            response_2 = notifications_v1_notification_query_service_pb2.BrowseNotificationsResponse()
            requests_0: list[notifications_v1_notification_query_service_pb2.FindNotificationsRequest] = []
            for item_0 in request.dataset_version.measurements:
                outgoing_0 = notifications_v1_notification_query_service_pb2.FindNotificationsRequest(
                    context=request.context,
                    filter=notifications_v1_notification_query_service_pb2.FindNotificationsRequest.Filter(
                        created_after=item_0.observed_at,
                        region=request.details.destination.region
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.notifications_notification_query.FindNotifications(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = labeling_v1_labeling_task_validation_service_pb2.LintLabelingTasksRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.dataset_version.subject.display_name),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.dataset_version.subject.email)
                )
            )
            registered_1 = cast(
                labeling_v1_labeling_task_validation_service_pb2_grpc.LabelingTaskValidationServiceStub,
                deps.clients.registry['acme.labeling.v1.LabelingTaskValidationService']
            )
            response_1 = await registered_1.LintLabelingTasks(outgoing_1, timeout=deps.settings.timeout)
            command_2 = DatasetVersionCalculationQuoteDatasetVersion2Command(
                context=request.context,
                filter_region=request.details.destination.region,
                filter_created_after=response_1.labeling_task.sla.due_at,
                filter_owner_id=response_1.labeling_task.customer.label_set_id,
                filter_labels=dict(response_1.result.details)
            )
            outgoing_2 = to_dataset_version_calculation_quote_dataset_version2_command(command_2)
            response_2 = await deps.clients.notifications_notification_query.BrowseNotifications(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.labeling_task.requester.email
            if returned_1_0:
                response.dataset_version.subject.email = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.source
            response.dataset_version.source = echoed_1
            return response

    async def handle_simulate_dataset_version(
        self,
        request: datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionRequest
    ) -> datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionResponse:
        """Simulates a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'SimulateDatasetVersion',
                extra={'fields': {'correlation_id': request.dataset_version.correlation_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'SimulateDatasetVersion',
                {'correlation_id': request.dataset_version.correlation_id}
            )
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = documents_v1_document_service_pb2.ListDocumentsResponse()
            response_1 = metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesResponse()
            response_2 = identity_v1_user_service_pb2.CloneUserResponse()
            command_0 = DatasetVersionCalculationSimulateDatasetVersion0Command.model_validate(
                {
                    'context': request.context,
                    'filter_region': request.details.destination.region,
                    'filter_created_after': request.dataset_version.occurred_at,
                    'filter_owner_id': request.dataset_version_id
                }
            )
            outgoing_0 = to_dataset_version_calculation_simulate_dataset_version0_command(command_0)
            response_0 = await deps.clients.documents_document.ListDocuments(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.dataset_version.subject.email),
                    variables=dict(request.dataset_version.attributes)
                ),
                reason=request.reason
            )
            send_1 = partial(
                deps.clients.metrics_metric_series_notification.UnsubscribeMetricSeriesUpdates,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = identity_v1_user_service_pb2.CloneUserRequest(
                context=request.context,
                user=identity_v1_identity_pb2.User(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.dataset_version.subject.email)
                )
            )
            response_2 = await hooks.dataset_version_calculation_simulate_dataset_version2(
                deps.clients.identity_user,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.metric_series.dimensions.unit
            returned_1_0_part_1 = response.dataset_version.measurements.add()
            if returned_1_0:
                returned_1_0_part_1.unit = returned_1_0
            returned_1_1 = response_1.metric_series.owner.email
            if returned_1_1:
                response.dataset_version.subject.email = returned_1_1
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.user.attributes
            response.dataset_version.attributes.update(returned_2_1)
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.occurred_at
            response.dataset_version.occurred_at.CopyFrom(echoed_1)
            return response
