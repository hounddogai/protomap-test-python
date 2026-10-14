"""Functional operations behind ForecastModelValidationService."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.certificates.v1 import (
    certificate_calculation_service_pb2 as certificates_v1_certificate_calculation_service_pb2,
)
from acme.certificates.v1 import certificates_pb2 as certificates_v1_certificates_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import refs_pb2 as forecasting_v1_refs_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.patients.v1 import patient_query_service_pb2 as patients_v1_patient_query_service_pb2

from acme_data.domains.forecasting.adapters import ForecastModelValidationScoreForecastModel1Adapter
from acme_data.domains.forecasting.adapters import ForecastModelValidationScoreForecastModel1Port
from acme_data.domains.forecasting.adapters import ForecastModelValidationValidateForecastModel1Adapter
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.models import ForecastModelValidationPreviewForecastModel1Command
from acme_data.domains.forecasting.models import to_forecast_model_validation_preview_forecast_model1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_check_forecast_model_eligibility(
    deps: Dependencies,
    request: forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityRequest
) -> forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityResponse:
    """Checks a forecast model."""
    response = forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CheckForecastModelEligibility', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CheckForecastModelEligibility',
            {'reason': request.reason}
        )
        await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
        response_0 = forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioResponse()
        response_1 = certificates_v1_certificate_calculation_service_pb2.CalculateCertificateResponse()
        outgoing_0 = forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioRequest(
            context=request.context,
            scenario=forecasting_v1_forecasting_pb2.Scenario(
                requester=common_v1_contact_pb2.ContactInfo(email=request.forecast_model.owner.email)
            )
        )
        response_0 = await deps.clients.forecasting_scenario_calculation.QuoteScenario(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = certificates_v1_certificate_calculation_service_pb2.CalculateCertificateRequest(
            certificate=certificates_v1_certificates_pb2.Certificate(
                audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.scenario.audit.created_by),
                billing_address=common_v1_address_pb2.PostalAddress(recipient=request.forecast_model.address.recipient)
            ),
            context=request.context,
            details=certificates_v1_certificate_calculation_service_pb2.CalculateCertificateRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.forecast_model.address.region)
            )
        )
        steps_1 = [
            partial(
                deps.clients.certificates_certificate_calculation.CalculateCertificate,
                outgoing_1,
                timeout=deps.settings.timeout
            )
        ]
        results_1 = await run_steps(steps_1)
        response_1 = results_1[-1]
        returned_0_0 = response_0.scenario.audit.created_by
        if returned_0_0:
            response.forecast_model.audit.created_by = returned_0_0
        returned_0_1 = response_0.scenario.audit.updated_at
        if returned_0_1.ListFields():
            response.forecast_model.audit.updated_at.MergeFrom(returned_0_1)
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.certificate.audit.created_by
        if returned_1_1:
            response.forecast_model.audit.created_by = returned_1_1
        echoed_0 = request.forecast_model_id
        response.forecast_model.forecast_model_id = echoed_0
        echoed_1 = request.forecast_model.code
        response.forecast_model.code = echoed_1
        return response


async def handle_get_forecast_model_rules(
    deps: Dependencies,
    request: forecasting_v1_forecast_model_validation_service_pb2.GetForecastModelRulesRequest
) -> forecasting_v1_forecast_model_validation_service_pb2.GetForecastModelRulesResponse:
    """Returns a forecast model."""
    response = forecasting_v1_forecast_model_validation_service_pb2.GetForecastModelRulesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetForecastModelRules', extra={'fields': {'domain': 'forecasting'}})
        await deps.repository.audit(request.context.tenant_id, 'GetForecastModelRules', {})
        response_0 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse()
        response_1 = forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosResponse()
        outgoing_0 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest(
            annotations=dict(request.context.baggage),
            context=request.context
        )
        response_0 = await deps.clients.metrics_metric_series_export.ScheduleMetricSeriesExport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosRequest(
            context=request.context,
            scenario=forecasting_v1_forecasting_pb2.Scenario(
                assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
            )
        )
        response_1 = cast(forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosResponse, await deps.bus.request(
            'acme.forecasting.v1.ForecastModelValidationService/GetForecastModelRules/1', outgoing_1, deps.settings.timeout,
        ))
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.result.correlation_id = returned_0_1
        returned_1_0 = response_1.scenario.requester.email
        if returned_1_0:
            response.forecast_model.owner.email = returned_1_0
        returned_1_1 = response_1.scenario.assignee.user_id
        if returned_1_1:
            response.forecast_model.owner.user_id = returned_1_1
        echoed_0 = request.forecast_model_id
        response.forecast_model.forecast_model_id = echoed_0
        return response


async def handle_lint_forecast_models(
    deps: Dependencies,
    request: forecasting_v1_forecast_model_validation_service_pb2.LintForecastModelsRequest
) -> forecasting_v1_forecast_model_validation_service_pb2.LintForecastModelsResponse:
    """Lints a forecast model."""
    response = forecasting_v1_forecast_model_validation_service_pb2.LintForecastModelsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('LintForecastModels', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'LintForecastModels', {'reason': request.reason})
        await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
        response_0 = forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsResponse()
        response_1 = lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationResponse()
        response_2 = forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationResponse()
        response_3 = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioResponse()
        outgoing_0 = forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsRequest(
            context=request.context,
            scenario=forecasting_v1_forecasting_pb2.Scenario(
                requester=common_v1_contact_pb2.ContactInfo(
                    email=request.forecast_model.owner.email,
                    preferred_channel=request.details.contact.preferred_channel
                )
            )
        )
        response_0 = await deps.clients.forecasting_scenario_calculation.CompareScenarioOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.scenario.audit.created_at),
                requester=common_v1_contact_pb2.ContactInfo(name=request.details.contact.name)
            )
        )
        method_name_1 = 'ExplainImpactCalculation'
        response_1 = await getattr(
            deps.clients.lineage_impact_calculation,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        outgoing_2 = forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.scenario.requester.email = request.forecast_model.owner.email
        if response_1.impact.WhichOneof('origin') == 'customer':
            outgoing_2.details.contact.email = response_1.impact.customer.email
        response_2 = await deps.clients.forecasting_scenario_calculation.ExplainScenarioCalculation(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest(
            context=request.context,
            scenario=forecasting_v1_forecasting_pb2.Scenario(
                customer=forecasting_v1_refs_pb2.ForecastModelRef(code=response_2.scenario.customer.code),
                requester=common_v1_contact_pb2.ContactInfo(name=request.details.contact.name),
                sla=forecasting_v1_forecasting_pb2.ScenarioSla(due_at=response_0.scenario.sla.due_at)
            )
        )
        document_3 = MessageToDict(outgoing_3, preserving_proto_field_name=True)
        outgoing_3 = ParseDict(document_3, forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest())
        response_3 = await deps.clients.forecasting_scenario_calculation.EstimateScenario(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.scenario.customer.display_name
        if returned_0_0:
            response.forecast_model.owner.display_name = returned_0_0
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.outcome.message = returned_0_1
        returned_1_0 = response_1.impact.assignee.user_id
        if returned_1_0:
            response.forecast_model.owner.user_id = returned_1_0
        returned_2_0 = response_2.result.details
        response.result.details.update(returned_2_0)
        returned_3_0 = response_3.scenario.audit.created_at
        if returned_3_0.ListFields():
            response.forecast_model.audit.created_at.MergeFrom(returned_3_0)
        returned_3_1 = response_3.scenario.assignee.display_name
        if returned_3_1:
            response.forecast_model.owner.display_name = returned_3_1
        echoed_0 = request.forecast_model_id
        response.forecast_model.forecast_model_id = echoed_0
        echoed_1 = request.forecast_model.status
        response.forecast_model.status = echoed_1
        return response


async def handle_normalize_forecast_model(
    deps: Dependencies,
    request: forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelRequest
) -> forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelResponse:
    """Normalizes a forecast model."""
    response = forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('NormalizeForecastModel', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'NormalizeForecastModel', {'reason': request.reason})
        await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
        response_0 = metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportResponse()
        response_1 = forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosResponse()
        response_2 = forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsResponse()
        response_3 = documents_v1_document_query_service_pb2.ExportDocumentsResponse()
        outgoing_0 = metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportRequest(
            context=request.context,
            details=metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportRequest.Details(
                recipient=common_v1_contact_pb2.ContactInfo(
                    email=request.details.contact.email,
                    name=request.details.contact.name,
                    preferred_channel=request.details.contact.preferred_channel
                )
            )
        )
        response_0 = await deps.clients.metrics_metric_alert_export.ShareMetricAlertExport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.scenario.customer.display_name = request.forecast_model.owner.display_name
        outgoing_1.scenario.assignee.user_id = response_0.metric_alert.owner.user_id
        outgoing_1.scenario.assignee.email = request.forecast_model.owner.email
        merged_1 = forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosRequest()
        merged_1.MergeFrom(outgoing_1)
        outgoing_1.CopyFrom(merged_1)
        response_1 = await deps.clients.forecasting_scenario_calculation.RecalculateScenarios(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsRequest(
            context=request.context,
            scenario=forecasting_v1_forecasting_pb2.Scenario(
                assignee=identity_v1_refs_pb2.UserRef(email=response_1.scenario.requester.email),
                sla=forecasting_v1_forecasting_pb2.ScenarioSla(paused_for=response_1.scenario.sla.paused_for)
            )
        )
        envelope_2 = AnyMessage()
        envelope_2.Pack(outgoing_2)
        outgoing_2 = forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsRequest()
        if not envelope_2.Unpack(outgoing_2):
            raise ValueError("partner envelope contains the wrong request type")
        response_2 = await deps.clients.forecasting_scenario_calculation.CompareScenarioOptions(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = documents_v1_document_query_service_pb2.ExportDocumentsRequest(
            context=request.context,
            filter=documents_v1_document_query_service_pb2.ExportDocumentsRequest.Filter(
                created_after=response_1.scenario.audit.updated_at,
                labels=dict(response_2.scenario.custom_fields),
                owner_id=request.forecast_model.owner.user_id,
                region=request.forecast_model.address.region
            )
        )
        async for chunk_3 in deps.clients.documents_document_query.ExportDocuments(
            outgoing_3,
            timeout=deps.settings.timeout
        ):
            response_3 = chunk_3
        returned_0_0 = response_0.outcome.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_1_0 = response_1.scenario.audit.created_by
        if returned_1_0:
            response.forecast_model.audit.created_by = returned_1_0
        returned_1_1 = response_1.scenario.audit.updated_at
        if returned_1_1.ListFields():
            response.forecast_model.audit.updated_at.MergeFrom(returned_1_1)
        returned_2_0 = response_2.scenario.customer.display_name
        if returned_2_0:
            response.forecast_model.owner.display_name = returned_2_0
        returned_2_1 = response_2.result.status
        if returned_2_1:
            response.result.status = returned_2_1
        echoed_0 = request.forecast_model_id
        response.forecast_model.forecast_model_id = echoed_0
        echoed_1 = request.forecast_model.capacity
        response.forecast_model.capacity = echoed_1
        return response


async def handle_preview_forecast_model(
    deps: Dependencies,
    request: forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelRequest
) -> forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelResponse:
    """Previews a forecast model."""
    response = forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PreviewForecastModel', extra={'fields': {'forecast_model_id': request.forecast_model_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'PreviewForecastModel',
            {'forecast_model_id': request.forecast_model_id}
        )
        await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
        response_0 = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioResponse()
        response_1 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse()
        response_2 = forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosResponse()
        response_3 = forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioResponse()
        outgoing_0 = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest(
            context=request.context,
            scenario=forecasting_v1_forecasting_pb2.Scenario(
                assignee=identity_v1_refs_pb2.UserRef(user_id=request.forecast_model.owner.user_id),
                customer=forecasting_v1_refs_pb2.ForecastModelRef(
                    display_name=request.forecast_model.owner.display_name
                ),
                requester=common_v1_contact_pb2.ContactInfo(
                    name=request.details.contact.name,
                    phone=request.details.contact.phone
                )
            )
        )
        response_0 = await deps.clients.forecasting_scenario_calculation.EstimateScenario(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = ForecastModelValidationPreviewForecastModel1Command.model_validate(
            {'context': request.context, 'reason': request.reason}
        )
        outgoing_1 = to_forecast_model_validation_preview_forecast_model1_command(command_1)
        response_1 = await deps.clients.metrics_metric_series_export.ScheduleMetricSeriesExport(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosRequest(
            context=request.context,
            scenario=forecasting_v1_forecasting_pb2.Scenario(
                audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.scenario.audit.created_by),
                customer=forecasting_v1_refs_pb2.ForecastModelRef(
                    code=response_0.scenario.customer.code,
                    display_name=request.forecast_model.owner.display_name
                )
            )
        )
        send_2 = partial(
            deps.clients.forecasting_scenario_calculation.RecalculateScenarios,
            timeout=deps.settings.timeout
        )
        response_2 = await send_2(outgoing_2)
        outgoing_3 = forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioRequest()
        outgoing_3.context.CopyFrom(request.context)
        if response_0.scenario.WhichOneof('origin') == 'customer':
            outgoing_3.scenario.assignee.display_name = response_0.scenario.customer.display_name
        outgoing_3.scenario.requester.preferred_channel = response_2.scenario.requester.preferred_channel
        outgoing_3.scenario.audit.created_by = response_0.scenario.audit.created_by
        response_3 = await deps.clients.forecasting_scenario_calculation.SimulateScenario(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.scenario.assignee.email
        if returned_0_0:
            response.forecast_model.owner.email = returned_0_0
        returned_0_1 = response_0.scenario.audit.updated_by
        if returned_0_1:
            response.forecast_model.audit.updated_by = returned_0_1
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.result.message = returned_2_0
        returned_2_1 = response_2.scenario.assignee.display_name
        if returned_2_1:
            response.forecast_model.owner.display_name = returned_2_1
        returned_3_0 = response_3.scenario.audit.updated_at
        if returned_3_0.ListFields():
            response.forecast_model.audit.updated_at.MergeFrom(returned_3_0)
        returned_3_1 = response_3.scenario.customer.forecast_model_id
        if returned_3_1:
            response.forecast_model.forecast_model_id = returned_3_1
        echoed_0 = request.forecast_model.specs
        response.forecast_model.specs.update(echoed_0)
        echoed_1 = request.forecast_model.name
        response.forecast_model.name = echoed_1
        return response


async def handle_score_forecast_model(
    deps: Dependencies,
    request: forecasting_v1_forecast_model_validation_service_pb2.ScoreForecastModelRequest
) -> forecasting_v1_forecast_model_validation_service_pb2.ScoreForecastModelResponse:
    """Scores a forecast model."""
    response = forecasting_v1_forecast_model_validation_service_pb2.ScoreForecastModelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScoreForecastModel', extra={'fields': {'currency_code': request.details.currency_code}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ScoreForecastModel',
            {'currency_code': request.details.currency_code}
        )
        await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
        response_0 = lineage_v1_impact_calculation_service_pb2.EstimateImpactResponse()
        response_1 = patients_v1_patient_query_service_pb2.SummarizePatientsResponse()
        outgoing_0 = lineage_v1_impact_calculation_service_pb2.EstimateImpactRequest(
            context=request.context,
            details=lineage_v1_impact_calculation_service_pb2.EstimateImpactRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(country_code=request.details.destination.country_code)
            )
        )
        response_0 = await deps.clients.lineage_impact_calculation.EstimateImpact(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = patients_v1_patient_query_service_pb2.SummarizePatientsRequest(
            annotations=dict(request.annotations),
            context=request.context,
            reason=request.reason
        )
        port_1: ForecastModelValidationScoreForecastModel1Port = ForecastModelValidationScoreForecastModel1Adapter(
            deps.clients.patients_patient_query,
            deps.settings.timeout
        )
        response_1 = await port_1.execute(outgoing_1)
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        returned_1_1 = response_1.result.correlation_id
        if returned_1_1:
            response.result.correlation_id = returned_1_1
        echoed_0 = request.forecast_model_id
        response.forecast_model.forecast_model_id = echoed_0
        echoed_1 = request.forecast_model.status
        response.forecast_model.status = echoed_1
        return response


async def handle_validate_forecast_model(
    deps: Dependencies,
    request: forecasting_v1_forecast_model_validation_service_pb2.ValidateForecastModelRequest
) -> forecasting_v1_forecast_model_validation_service_pb2.ValidateForecastModelResponse:
    """Validates a forecast model."""
    response = forecasting_v1_forecast_model_validation_service_pb2.ValidateForecastModelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidateForecastModel', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidateForecastModel', {'reason': request.reason})
        await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
        response_0 = forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioResponse()
        response_1 = forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastResponse()
        outgoing_0 = forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioRequest(
            context=request.context,
            scenario=forecasting_v1_forecasting_pb2.Scenario(
                assignee=identity_v1_refs_pb2.UserRef(email=request.details.contact.email),
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.forecast_model.audit.updated_at),
                customer=forecasting_v1_refs_pb2.ForecastModelRef(
                    display_name=request.forecast_model.owner.display_name
                ),
                requester=common_v1_contact_pb2.ContactInfo(name=request.details.contact.name)
            )
        )
        response_0 = await deps.clients.forecasting_scenario_calculation.SimulateScenario(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest(
            context=request.context,
            demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                billing_address=common_v1_address_pb2.PostalAddress(
                    postal_code=request.forecast_model.address.postal_code
                )
            )
        )
        response_1 = await ForecastModelValidationValidateForecastModel1Adapter(
            deps.clients.forecasting_demand_forecast_validation,
            deps.settings.timeout
        )(outgoing_1)
        returned_0_0 = response_0.scenario.audit.updated_at
        if returned_0_0.ListFields():
            response.forecast_model.audit.updated_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.scenario.assignee.user_id
        if returned_0_1:
            response.forecast_model.owner.user_id = returned_0_1
        returned_1_0 = response_1.demand_forecast.audit.created_at
        if returned_1_0.ListFields():
            response.forecast_model.audit.created_at.MergeFrom(returned_1_0)
        echoed_0 = request.forecast_model_id
        response.forecast_model.forecast_model_id = echoed_0
        echoed_1 = request.forecast_model.status
        response.forecast_model.status = echoed_1
        return response
