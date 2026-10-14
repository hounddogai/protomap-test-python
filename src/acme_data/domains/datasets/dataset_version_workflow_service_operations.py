"""Functional operations behind DatasetVersionWorkflowService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
import asyncio
import logging

from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_version_approval_service_pb2 as datasets_v1_dataset_version_approval_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import dataset_version_workflow_service_pb2 as datasets_v1_dataset_version_workflow_service_pb2
from acme.datasets.v1 import dataset_workflow_service_pb2 as datasets_v1_dataset_workflow_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.lineage.v1 import impact_approval_service_pb2 as lineage_v1_impact_approval_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.orders.v1 import order_calculation_service_pb2 as orders_v1_order_calculation_service_pb2
from acme.orders.v1 import orders_pb2 as orders_v1_orders_pb2

from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_advance_dataset_version_workflow(
    deps: Dependencies,
    request: datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowRequest
) -> datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowResponse:
    """Advances a dataset version."""
    response = datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('AdvanceDatasetVersionWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'AdvanceDatasetVersionWorkflow',
            {'reason': request.reason}
        )
        await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
        response_0 = datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionResponse()
        response_1 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionResponse()
        outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                source=request.dataset_version.source,
                subject=customers_v1_refs_pb2.CustomerRef(
                    display_name=request.dataset_version.subject.display_name,
                    email=request.details.notify.email
                )
            )
        )
        response_0 = await deps.clients.datasets_dataset_version_calculation.QuoteDatasetVersion(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        requests_1: list[datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest] = []
        for item_1 in request.dataset_version.measurements:
            outgoing_1 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    measurements=[
                        datasets_v1_datasets_pb2.DatasetVersionMeasurement(
                            metric=item_1.metric,
                            observed_at=item_1.observed_at
                        )
                    ]
                )
            )
            requests_1.append(outgoing_1)
        replies_1 = await asyncio.gather(*(
            deps.clients.datasets_dataset_version_validation.ExplainDatasetVersionDecision(
                entry,
                timeout=deps.settings.timeout
            ) for entry in requests_1
        ))
        if replies_1:
            response_1 = replies_1[-1]
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_0_1 = response_0.dataset_version.sequence
        if returned_0_1:
            response.dataset_version.sequence = returned_0_1
        echoed_0 = request.dataset_version_id
        response.dataset_version.dataset_version_id = echoed_0
        echoed_1 = request.dataset_version.occurred_at
        response.dataset_version.occurred_at.CopyFrom(echoed_1)
        return response


async def handle_cancel_dataset_version_workflow(
    deps: Dependencies,
    request: datasets_v1_dataset_version_workflow_service_pb2.CancelDatasetVersionWorkflowRequest
) -> datasets_v1_dataset_version_workflow_service_pb2.CancelDatasetVersionWorkflowResponse:
    """Cancels a dataset version."""
    response = datasets_v1_dataset_version_workflow_service_pb2.CancelDatasetVersionWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CancelDatasetVersionWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CancelDatasetVersionWorkflow',
            {'reason': request.reason}
        )
        await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
        response_0 = orders_v1_order_calculation_service_pb2.QuoteOrderResponse()
        response_1 = customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordResponse()
        outgoing_0 = orders_v1_order_calculation_service_pb2.QuoteOrderRequest(
            context=request.context,
            order=orders_v1_orders_pb2.Order(
                counterparty=customers_v1_refs_pb2.CustomerRef(
                    customer_id=request.dataset_version.subject.customer_id,
                    display_name=request.dataset_version.subject.display_name
                ),
                lines=[orders_v1_orders_pb2.OrderLine(attributes=dict(request.dataset_version.attributes))]
            )
        )
        response_0 = await deps.clients.orders_order_calculation.QuoteOrder(outgoing_0, timeout=deps.settings.timeout)
        callbacks_1: list[
            Callable[[], Awaitable[customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordResponse]]
        ] = []
        for item_1 in request.dataset_version.measurements:
            outgoing_1 = customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    measurements=[
                        customers_v1_customers_pb2.ConsentRecordMeasurement(
                            metric=item_1.metric,
                            observed_at=item_1.observed_at,
                            unit=item_1.unit,
                            value=item_1.value
                        )
                    ]
                ),
                context=request.context
            )
            async def send_1(
                payload: customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordRequest = outgoing_1
            ) -> customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordResponse:
                return await deps.clients.customers_consent_record_calculation.EstimateConsentRecord(
                    payload,
                    timeout=deps.settings.timeout
                )
            callbacks_1.append(send_1)
        for callback_1 in callbacks_1:
            response_1 = await callback_1()
        returned_0_0 = response_0.order.counterparty.email
        if returned_0_0:
            response.dataset_version.subject.email = returned_0_0
        echoed_0 = request.dataset_version_id
        response.dataset_version.dataset_version_id = echoed_0
        echoed_1 = request.dataset_version.sequence
        response.dataset_version.sequence = echoed_1
        return response


async def handle_inspect_dataset_version_workflow(
    deps: Dependencies,
    request: datasets_v1_dataset_version_workflow_service_pb2.InspectDatasetVersionWorkflowRequest
) -> datasets_v1_dataset_version_workflow_service_pb2.InspectDatasetVersionWorkflowResponse:
    """Returns a dataset version."""
    response = datasets_v1_dataset_version_workflow_service_pb2.InspectDatasetVersionWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('InspectDatasetVersionWorkflow', extra={'fields': {'locale': request.context.locale}})
        await deps.repository.audit(
            request.context.tenant_id,
            'InspectDatasetVersionWorkflow',
            {'locale': request.context.locale}
        )
        echoed_0 = request.dataset_version_id
        response.dataset_version.dataset_version_id = echoed_0
        return response


async def handle_pause_dataset_version_workflow(
    deps: Dependencies,
    request: datasets_v1_dataset_version_workflow_service_pb2.PauseDatasetVersionWorkflowRequest
) -> datasets_v1_dataset_version_workflow_service_pb2.PauseDatasetVersionWorkflowResponse:
    """Pauses a dataset version."""
    response = datasets_v1_dataset_version_workflow_service_pb2.PauseDatasetVersionWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PauseDatasetVersionWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'PauseDatasetVersionWorkflow',
            {'reason': request.reason}
        )
        await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
        response_0 = datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionResponse()
        response_1 = datasets_v1_dataset_version_approval_service_pb2.ListPendingDatasetVersionsResponse()
        response_2 = customers_v1_customer_service_pb2.CloneCustomerResponse()
        outgoing_0 = datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                subject=customers_v1_refs_pb2.CustomerRef(email=request.dataset_version.subject.email)
            )
        )
        response_0 = await deps.clients.datasets_dataset_version_validation.PreviewDatasetVersion(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        async for item_1 in async_messages(request.dataset_version.measurements):
            outgoing_1 = datasets_v1_dataset_version_approval_service_pb2.ListPendingDatasetVersionsRequest(
                context=request.context,
                filter=datasets_v1_dataset_version_approval_service_pb2.ListPendingDatasetVersionsRequest.Filter(
                    created_after=item_1.observed_at
                )
            )
            response_1 = await deps.clients.datasets_dataset_version_approval.ListPendingDatasetVersions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
        outgoing_2 = customers_v1_customer_service_pb2.CloneCustomerRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.customer.contact.preferred_channel = request.details.notify.preferred_channel
        outgoing_2.customer.contact.email = request.details.notify.email
        outgoing_2.customer.relationship_manager.email = response_0.dataset_version.subject.email
        outgoing_2.context.tenant_id = tenant_id.get()
        response_2 = await deps.clients.customers_customer.CloneCustomer(outgoing_2, timeout=deps.settings.timeout)
        returned_0_0 = response_0.dataset_version.correlation_id
        if returned_0_0:
            response.dataset_version.correlation_id = returned_0_0
        returned_0_1 = response_0.dataset_version.subject.email
        if returned_0_1:
            response.dataset_version.subject.email = returned_0_1
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.outcome.status = returned_2_0
        echoed_0 = request.dataset_version_id
        response.dataset_version.dataset_version_id = echoed_0
        echoed_1 = request.dataset_version.kind
        response.dataset_version.kind = echoed_1
        return response


async def handle_resume_dataset_version_workflow(
    deps: Dependencies,
    request: datasets_v1_dataset_version_workflow_service_pb2.ResumeDatasetVersionWorkflowRequest
) -> datasets_v1_dataset_version_workflow_service_pb2.ResumeDatasetVersionWorkflowResponse:
    """Resumes a dataset version."""
    response = datasets_v1_dataset_version_workflow_service_pb2.ResumeDatasetVersionWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info(
            'ResumeDatasetVersionWorkflow',
            extra={'fields': {'correlation_id': request.dataset_version.correlation_id}}
        )
        await deps.repository.audit(
            request.context.tenant_id,
            'ResumeDatasetVersionWorkflow',
            {'correlation_id': request.dataset_version.correlation_id}
        )
        await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
        response_0 = datasets_v1_dataset_query_service_pb2.SummarizeDatasetsResponse()
        response_1 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse()
        outgoing_0 = datasets_v1_dataset_query_service_pb2.SummarizeDatasetsRequest(
            annotations=dict(request.annotations),
            context=request.context,
            reason=request.reason
        )
        response_0 = await deps.clients.datasets_dataset_query.SummarizeDatasets(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                subject=customers_v1_refs_pb2.CustomerRef(email=request.details.notify.email)
            )
        )
        steps_1 = [
            partial(
                deps.clients.datasets_dataset_version_calculation.CalculateDatasetVersion,
                outgoing_1,
                timeout=deps.settings.timeout
            )
        ]
        results_1 = await run_steps(steps_1)
        response_1 = results_1[-1]
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_1_0 = response_1.dataset_version.sequence
        if returned_1_0:
            response.dataset_version.sequence = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        echoed_0 = request.dataset_version_id
        response.dataset_version.dataset_version_id = echoed_0
        echoed_1 = request.dataset_version.attributes
        response.dataset_version.attributes.update(echoed_1)
        return response


async def handle_retry_dataset_version_workflow(
    deps: Dependencies,
    request: datasets_v1_dataset_version_workflow_service_pb2.RetryDatasetVersionWorkflowRequest
) -> datasets_v1_dataset_version_workflow_service_pb2.RetryDatasetVersionWorkflowResponse:
    """Retrys a dataset version."""
    response = datasets_v1_dataset_version_workflow_service_pb2.RetryDatasetVersionWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RetryDatasetVersionWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'RetryDatasetVersionWorkflow',
            {'reason': request.reason}
        )
        await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
        response_0 = featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportResponse()
        outgoing_0 = featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest(
            context=request.context,
            details=featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
            )
        )
        response_0 = await deps.clients.featurestore_feature_value_import.RetryFeatureValueImport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.feature_value.attributes
        response.dataset_version.attributes.update(returned_0_1)
        echoed_0 = request.dataset_version_id
        response.dataset_version.dataset_version_id = echoed_0
        echoed_1 = request.dataset_version.correlation_id
        response.dataset_version.correlation_id = echoed_1
        return response


async def handle_start_dataset_version_workflow(
    deps: Dependencies,
    request: datasets_v1_dataset_version_workflow_service_pb2.StartDatasetVersionWorkflowRequest
) -> datasets_v1_dataset_version_workflow_service_pb2.StartDatasetVersionWorkflowResponse:
    """Starts a dataset version."""
    response = datasets_v1_dataset_version_workflow_service_pb2.StartDatasetVersionWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('StartDatasetVersionWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'StartDatasetVersionWorkflow',
            {'reason': request.reason}
        )
        await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
        response_0 = customers_v1_customer_service_pb2.WatchCustomersResponse()
        response_1 = lineage_v1_impact_approval_service_pb2.ListPendingImpactsResponse()
        response_2 = datasets_v1_dataset_workflow_service_pb2.AdvanceDatasetWorkflowResponse()
        response_3 = metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityResponse()
        outgoing_0 = customers_v1_customer_service_pb2.WatchCustomersRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
        )
        async for chunk_0 in deps.clients.customers_customer.WatchCustomers(outgoing_0, timeout=deps.settings.timeout):
            response_0 = chunk_0
        for item_1 in request.dataset_version.measurements:
            outgoing_1 = lineage_v1_impact_approval_service_pb2.ListPendingImpactsRequest(
                context=request.context,
                filter=lineage_v1_impact_approval_service_pb2.ListPendingImpactsRequest.Filter(
                    created_after=item_1.observed_at
                )
            )
            response_1 = await deps.clients.lineage_impact_approval.ListPendingImpacts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
        requests_2: list[datasets_v1_dataset_workflow_service_pb2.AdvanceDatasetWorkflowRequest] = []
        for item_2 in request.dataset_version.measurements:
            outgoing_2 = datasets_v1_dataset_workflow_service_pb2.AdvanceDatasetWorkflowRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    dimensions=datasets_v1_datasets_pb2.DatasetDimensions(unit=item_2.unit)
                )
            )
            requests_2.append(outgoing_2)
        replies_2 = await asyncio.gather(*(
            deps.clients.datasets_dataset_workflow.AdvanceDatasetWorkflow(
                entry,
                timeout=deps.settings.timeout
            ) for entry in requests_2
        ))
        if replies_2:
            response_2 = replies_2[-1]
        fields_3: dict[str, Any] = {
            'context': request.context,
            'details': {
                'contact': {
                    'email': request.dataset_version.subject.email,
                    'preferred_channel': request.details.notify.preferred_channel
                }
            },
            'metric_series': {
                'address': {'recipient': response_2.dataset.address.recipient},
                'dimensions': {'height': response_2.dataset.dimensions.height}
            }
        }
        outgoing_3 = metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityRequest(**fields_3)
        response_3 = await deps.clients.metrics_metric_series_validation.CheckMetricSeriesEligibility(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_3_0 = response_3.metric_series.owner.email
        if returned_3_0:
            response.dataset_version.subject.email = returned_3_0
        returned_3_1 = response_3.outcome.status
        if returned_3_1:
            response.outcome.status = returned_3_1
        echoed_0 = request.dataset_version_id
        response.dataset_version.dataset_version_id = echoed_0
        echoed_1 = request.dataset_version.kind
        response.dataset_version.kind = echoed_1
        return response
