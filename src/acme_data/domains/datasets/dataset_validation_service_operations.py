"""Functional operations behind DatasetValidationService."""

from __future__ import annotations

from functools import partial
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.appointments.v1 import appointment_service_pb2 as appointments_v1_appointment_service_pb2
from acme.appointments.v1 import appointments_pb2 as appointments_v1_appointments_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_query_service_pb2 as pipelines_v1_pipeline_run_query_service_pb2
from acme.shows.v1 import show_calculation_service_pb2 as shows_v1_show_calculation_service_pb2

from acme_data.domains.datasets import hooks
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.domains.datasets.models import DatasetValidationCheckDatasetEligibility1Command
from acme_data.domains.datasets.models import DatasetValidationScoreDataset2Command
from acme_data.domains.datasets.models import to_dataset_validation_check_dataset_eligibility1_command
from acme_data.domains.datasets.models import to_dataset_validation_score_dataset2_command
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_check_dataset_eligibility(
    deps: Dependencies,
    request: datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest
) -> datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityResponse:
    """Checks a dataset."""
    response = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CheckDatasetEligibility', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CheckDatasetEligibility', {'reason': request.reason})
        await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
        response_0 = datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionResponse()
        response_1 = metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsResponse()
        response_2 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationResponse()
        response_3 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse()
        outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                measurements=[datasets_v1_datasets_pb2.DatasetVersionMeasurement(unit=request.dataset.dimensions.unit)],
                subject=customers_v1_refs_pb2.CustomerRef(email=request.details.contact.email)
            ),
            details=datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(lines=list(request.dataset.address.lines))
            )
        )
        response_0 = await deps.clients.datasets_dataset_version_calculation.QuoteDatasetVersion(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = DatasetValidationCheckDatasetEligibility1Command.model_validate(
            {
                'context': request.context,
                'filter_region': request.dataset.address.region,
                'filter_created_after': request.dataset.audit.created_at
            }
        )
        outgoing_1 = to_dataset_validation_check_dataset_eligibility1_command(command_1)
        response_1 = await deps.clients.metrics_metric_alert_export.ListMetricAlertExports(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                measurements=[datasets_v1_datasets_pb2.DatasetVersionMeasurement(unit=request.dataset.dimensions.unit)],
                subject=customers_v1_refs_pb2.CustomerRef(email=response_0.dataset_version.subject.email)
            ),
            details=datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.details.contact.email,
                    phone=request.details.contact.phone
                )
            )
        )
        send_2 = partial(
            deps.clients.datasets_dataset_version_calculation.ExplainDatasetVersionCalculation,
            timeout=deps.settings.timeout
        )
        response_2 = await send_2(outgoing_2)
        outgoing_3 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                subject=customers_v1_refs_pb2.CustomerRef(
                    display_name=request.dataset.owner.display_name,
                    email=request.details.contact.email
                )
            )
        )
        response_3 = await hooks.dataset_validation_check_dataset_eligibility3(
            deps.clients.datasets_dataset_version_calculation,
            outgoing_3,
            deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.outcome.status = returned_0_1
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        returned_1_1 = response_1.result.message
        if returned_1_1:
            response.result.message = returned_1_1
        returned_2_0 = response_2.outcome.next_steps
        response.outcome.next_steps.extend(returned_2_0)
        returned_3_0 = response_3.result.message
        if returned_3_0:
            response.outcome.message = returned_3_0
        echoed_0 = request.dataset_id
        response.dataset.dataset_id = echoed_0
        echoed_1 = request.dataset.owner
        response.dataset.owner.CopyFrom(echoed_1)
        return response


async def handle_explain_dataset_decision(
    deps: Dependencies,
    request: datasets_v1_dataset_validation_service_pb2.ExplainDatasetDecisionRequest
) -> datasets_v1_dataset_validation_service_pb2.ExplainDatasetDecisionResponse:
    """Explains a dataset."""
    response = datasets_v1_dataset_validation_service_pb2.ExplainDatasetDecisionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExplainDatasetDecision', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ExplainDatasetDecision', {'reason': request.reason})
        await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
        response_0 = notifications_v1_notification_validation_service_pb2.LintNotificationsResponse()
        response_1 = labeling_v1_label_set_calculation_service_pb2.SimulateLabelSetResponse()
        response_2 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse()
        outgoing_0 = notifications_v1_notification_validation_service_pb2.LintNotificationsRequest(
            context=request.context,
            details=notifications_v1_notification_validation_service_pb2.LintNotificationsRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
            )
        )
        response_0 = await deps.clients.notifications_notification_validation.LintNotifications(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = labeling_v1_label_set_calculation_service_pb2.SimulateLabelSetRequest()
        outgoing_1.context.CopyFrom(request.context)
        field_1_1_part_1 = outgoing_1.label_set.children.add()
        field_1_1_part_2 = field_1_1_part_1.children.add()
        field_1_1_part_2.manager.user_id = response_0.notification.assignee.user_id
        if response_0.notification.WhichOneof('origin') == 'customer':
            field_1_2_part_1 = outgoing_1.label_set.children.add()
            field_1_2_part_2 = field_1_2_part_1.children.add()
            field_1_2_part_2.manager.display_name = response_0.notification.customer.display_name
        field_1_3_part_1 = outgoing_1.label_set.children.add()
        field_1_3_part_2 = field_1_3_part_1.children.add()
        field_1_3_part_2.audit.updated_at.CopyFrom(response_0.notification.audit.updated_at)
        response_1 = await deps.clients.labeling_label_set_calculation.SimulateLabelSet(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                subject=customers_v1_refs_pb2.CustomerRef(
                    display_name=request.dataset.owner.display_name,
                    email=response_1.label_set.manager.email
                )
            ),
            details=datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(recipient=response_1.label_set.location.recipient)
            )
        )
        steps_2 = [
            partial(
                deps.clients.datasets_dataset_version_calculation.CompareDatasetVersionOptions,
                outgoing_2,
                timeout=deps.settings.timeout
            )
        ]
        results_2 = await run_steps(steps_2)
        response_2 = results_2[-1]
        returned_0_0 = response_0.notification.audit.created_at
        if returned_0_0.ListFields():
            response.dataset.audit.created_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.outcome.message
        if returned_0_1:
            response.outcome.message = returned_0_1
        returned_1_0 = response_1.label_set.name
        if returned_1_0:
            response.dataset.name = returned_1_0
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.result.message = returned_2_0
        returned_2_1 = response_2.dataset_version.subject.display_name
        if returned_2_1:
            response.dataset.owner.display_name = returned_2_1
        echoed_0 = request.dataset_id
        response.dataset.dataset_id = echoed_0
        echoed_1 = request.dataset.code
        response.dataset.code = echoed_1
        return response


async def handle_get_dataset_rules(
    deps: Dependencies,
    request: datasets_v1_dataset_validation_service_pb2.GetDatasetRulesRequest
) -> datasets_v1_dataset_validation_service_pb2.GetDatasetRulesResponse:
    """Returns a dataset."""
    response = datasets_v1_dataset_validation_service_pb2.GetDatasetRulesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetDatasetRules', extra={'fields': {'domain': 'datasets'}})
        await deps.repository.audit(request.context.tenant_id, 'GetDatasetRules', {})
        response_0 = lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeResponse()
        outgoing_0 = lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeRequest(
            context=request.context,
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                correlation_id=request.context.tenant_id,
                occurred_at=request.context.deadline,
                source=request.dataset_id
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_calculation.CalculateLineageEdge(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.lineage_edge.subject.display_name
        if returned_0_0:
            response.dataset.owner.display_name = returned_0_0
        echoed_0 = request.dataset_id
        response.dataset.dataset_id = echoed_0
        return response


async def handle_lint_datasets(
    deps: Dependencies,
    request: datasets_v1_dataset_validation_service_pb2.LintDatasetsRequest
) -> datasets_v1_dataset_validation_service_pb2.LintDatasetsResponse:
    """Lints a dataset."""
    response = datasets_v1_dataset_validation_service_pb2.LintDatasetsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('LintDatasets', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'LintDatasets', {'reason': request.reason})
        await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
        response_0 = shows_v1_show_calculation_service_pb2.EstimateShowResponse()
        response_1 = appointments_v1_appointment_service_pb2.CloneAppointmentResponse()
        outgoing_0 = shows_v1_show_calculation_service_pb2.EstimateShowRequest()
        outgoing_0.context.CopyFrom(request.context)
        field_0_1_part_1 = outgoing_0.show.participants.add()
        field_0_1_part_1.contact.email = request.details.contact.email
        if request.dataset.WhichOneof('locator') == 'address':
            outgoing_0.show.location.postal_code = request.dataset.address.postal_code
        outgoing_0.show.audit.created_at.CopyFrom(request.dataset.audit.created_at)
        response_0 = await deps.clients.shows_show_calculation.EstimateShow(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = appointments_v1_appointment_service_pb2.CloneAppointmentRequest(
            appointment=appointments_v1_appointments_pb2.Appointment(
                audit=common_v1_audit_pb2.AuditInfo(created_by=request.dataset.audit.created_by),
                participants=[
                    appointments_v1_appointments_pb2.AppointmentParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=response_0.show.organizer.email,
                            name=request.details.contact.name
                        )
                    )
                ]
            ),
            context=request.context
        )
        response_1 = await deps.clients.appointments_appointment.CloneAppointment(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.show.audit.updated_at
        if returned_0_0.ListFields():
            response.dataset.audit.updated_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.result.details
        response.result.details.update(returned_0_1)
        returned_1_0 = response_1.appointment.organizer.user_id
        if returned_1_0:
            response.dataset.owner.user_id = returned_1_0
        returned_1_1 = response_1.result.status
        if returned_1_1:
            response.result.status = returned_1_1
        echoed_0 = request.dataset_id
        response.dataset.dataset_id = echoed_0
        echoed_1 = request.dataset.capacity
        response.dataset.capacity = echoed_1
        return response


async def handle_normalize_dataset(
    deps: Dependencies,
    request: datasets_v1_dataset_validation_service_pb2.NormalizeDatasetRequest
) -> datasets_v1_dataset_validation_service_pb2.NormalizeDatasetResponse:
    """Normalizes a dataset."""
    response = datasets_v1_dataset_validation_service_pb2.NormalizeDatasetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('NormalizeDataset', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'NormalizeDataset', {'reason': request.reason})
        await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
        response_0 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationResponse()
        response_1 = lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeResponse()
        response_2 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse()
        response_3 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse()
        outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                subject=customers_v1_refs_pb2.CustomerRef(email=request.dataset.owner.email)
            ),
            details=datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    name=request.details.contact.name,
                    preferred_channel=request.details.contact.preferred_channel
                ),
                locale=request.details.locale
            )
        )
        response_0 = await deps.clients.datasets_dataset_version_calculation.ExplainDatasetVersionCalculation(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeRequest()
        outgoing_1.context.CopyFrom(request.context)
        if request.dataset.WhichOneof('locator') == 'address':
            outgoing_1.details.destination.country_code = request.dataset.address.country_code
        if request.dataset.WhichOneof('locator') == 'address':
            outgoing_1.details.destination.locality = request.dataset.address.locality
        response_1 = await deps.clients.lineage_lineage_edge_calculation.CalculateLineageEdge(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                subject=customers_v1_refs_pb2.CustomerRef(display_name=response_0.dataset_version.subject.display_name)
            ),
            details=datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.dataset.address.region)
            )
        )
        document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
        outgoing_2 = ParseDict(
            document_2,
            datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest()
        )
        response_2 = await deps.clients.datasets_dataset_version_calculation.CalculateDatasetVersion(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                subject=customers_v1_refs_pb2.CustomerRef(display_name=response_2.dataset_version.subject.display_name)
            ),
            details=datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    locality=request.dataset.address.locality,
                    region=request.dataset.address.region
                )
            )
        )
        document_3 = MessageToJson(outgoing_3, preserving_proto_field_name=True)
        outgoing_3 = Parse(
            document_3,
            datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest()
        )
        response_3 = await deps.clients.datasets_dataset_version_calculation.CompareDatasetVersionOptions(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.dataset_version.subject.email
        if returned_0_0:
            response.dataset.owner.email = returned_0_0
        returned_0_1 = response_0.outcome.status
        if returned_0_1:
            response.result.status = returned_0_1
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        returned_1_1 = response_1.result.message
        if returned_1_1:
            response.result.message = returned_1_1
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.outcome.status = returned_2_0
        returned_2_1 = response_2.result.details
        response.result.details.update(returned_2_1)
        returned_3_0 = response_3.result.status
        if returned_3_0:
            response.outcome.status = returned_3_0
        echoed_0 = request.dataset_id
        response.dataset.dataset_id = echoed_0
        echoed_1 = request.dataset.name
        response.dataset.name = echoed_1
        return response


async def handle_preview_dataset(
    deps: Dependencies,
    request: datasets_v1_dataset_validation_service_pb2.PreviewDatasetRequest
) -> datasets_v1_dataset_validation_service_pb2.PreviewDatasetResponse:
    """Previews a dataset."""
    response = datasets_v1_dataset_validation_service_pb2.PreviewDatasetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PreviewDataset', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PreviewDataset', {'reason': request.reason})
        await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
        response_0 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsResponse()
        response_1 = notifications_v1_notification_query_service_pb2.ResolveNotificationsResponse()
        outgoing_0 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest(
            context=request.context,
            filter=metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest.Filter(
                created_after=request.dataset.audit.updated_at,
                region=request.dataset.address.region
            )
        )
        outgoing_1 = notifications_v1_notification_query_service_pb2.ResolveNotificationsRequest(
            context=request.context
        )
        response_0, response_1 = await asyncio.gather(
            deps.clients.metrics_metric_alert_query.BrowseMetricAlerts(outgoing_0, timeout=deps.settings.timeout),
            deps.clients.notifications_notification_query.ResolveNotifications(
                outgoing_1,
                timeout=deps.settings.timeout
            ),
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.outcome.status = returned_0_1
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        returned_1_1 = response_1.result.status
        if returned_1_1:
            response.result.status = returned_1_1
        echoed_0 = request.dataset_id
        response.dataset.dataset_id = echoed_0
        echoed_1 = request.dataset.capacity
        response.dataset.capacity = echoed_1
        return response


async def handle_score_dataset(
    deps: Dependencies,
    request: datasets_v1_dataset_validation_service_pb2.ScoreDatasetRequest
) -> datasets_v1_dataset_validation_service_pb2.ScoreDatasetResponse:
    """Scores a dataset."""
    response = datasets_v1_dataset_validation_service_pb2.ScoreDatasetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScoreDataset', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ScoreDataset', {'reason': request.reason})
        await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
        response_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse()
        response_1 = pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsResponse()
        response_2 = pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunResponse()
        outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                measurements=[datasets_v1_datasets_pb2.DatasetVersionMeasurement(unit=request.dataset.dimensions.unit)]
            )
        )
        response_0 = await deps.clients.datasets_dataset_version_calculation.CompareDatasetVersionOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsRequest()
        outgoing_1.context.CopyFrom(request.context)
        if request.dataset.WhichOneof('locator') == 'address':
            outgoing_1.filter.region = request.dataset.address.region
        outgoing_1.filter.owner_id = request.dataset.owner.user_id
        outgoing_1.filter.created_after.CopyFrom(request.dataset.audit.updated_at)
        outgoing_1.filter.labels.update(dict(request.annotations))
        response_1 = await deps.clients.pipelines_pipeline_run_query.BrowsePipelineRuns(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        command_2 = DatasetValidationScoreDataset2Command.model_validate(
            {
                'context': request.context,
                'details_destination_country_code': request.dataset.address.country_code,
                'details_destination_recipient': request.details.destination.recipient
            }
        )
        outgoing_2 = to_dataset_validation_score_dataset2_command(command_2)
        response_2 = await deps.clients.pipelines_pipeline_run_calculation.EstimatePipelineRun(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.dataset_version.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.dataset_version.subject.display_name
        if returned_0_1:
            response.dataset.owner.display_name = returned_0_1
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.result.status
        if returned_1_1:
            response.result.status = returned_1_1
        returned_2_0 = response_2.pipeline_run.audit.created_at
        if returned_2_0.ListFields():
            response.dataset.audit.created_at.MergeFrom(returned_2_0)
        echoed_0 = request.dataset_id
        response.dataset.dataset_id = echoed_0
        echoed_1 = request.dataset.specs
        response.dataset.specs.update(echoed_1)
        return response


async def handle_validate_dataset(
    deps: Dependencies,
    request: datasets_v1_dataset_validation_service_pb2.ValidateDatasetRequest
) -> datasets_v1_dataset_validation_service_pb2.ValidateDatasetResponse:
    """Validates a dataset."""
    response = datasets_v1_dataset_validation_service_pb2.ValidateDatasetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidateDataset', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidateDataset', {'reason': request.reason})
        await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
        response_0 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationResponse()
        response_1 = authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityResponse()
        outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                measurements=[datasets_v1_datasets_pb2.DatasetVersionMeasurement(unit=request.dataset.dimensions.unit)]
            )
        )
        response_0 = await deps.clients.datasets_dataset_version_calculation.ExplainDatasetVersionCalculation(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityRequest(
            access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.dataset.audit.created_at),
                owner=identity_v1_refs_pb2.UserRef(email=request.dataset.owner.email)
            ),
            context=request.context,
            details=authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    phone=request.details.contact.phone,
                    preferred_channel=request.details.contact.preferred_channel
                )
            )
        )
        response_1 = await hooks.dataset_validation_validate_dataset1(
            deps.clients.authorization_access_policy_validation,
            outgoing_1,
            deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_1_0 = response_1.access_policy.name
        if returned_1_0:
            response.dataset.name = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        echoed_0 = request.dataset_id
        response.dataset.dataset_id = echoed_0
        echoed_1 = request.dataset.capacity
        response.dataset.capacity = echoed_1
        return response
