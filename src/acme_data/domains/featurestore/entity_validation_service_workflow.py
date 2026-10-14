"""Application workflow for Entity Validation."""

from __future__ import annotations

from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.audit.v1 import audit_pb2 as audit_v1_audit_pb2
from acme.audit.v1 import refs_pb2 as audit_v1_refs_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import entity_validation_service_pb2 as featurestore_v1_entity_validation_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.patients.v1 import patient_calculation_service_pb2 as patients_v1_patient_calculation_service_pb2

from acme_data.domains.featurestore.adapters import EntityValidationNormalizeEntity0Adapter
from acme_data.domains.featurestore.adapters import EntityValidationNormalizeEntity0Port
from acme_data.domains.featurestore.adapters import EntityValidationNormalizeEntity2Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import EntityValidationExplainEntityDecision0Command
from acme_data.domains.featurestore.models import EntityValidationExplainEntityDecision1Command
from acme_data.domains.featurestore.models import to_entity_validation_explain_entity_decision0_command
from acme_data.domains.featurestore.models import to_entity_validation_explain_entity_decision1_command
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class EntityValidationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_check_entity_eligibility(
        self,
        request: featurestore_v1_entity_validation_service_pb2.CheckEntityEligibilityRequest
    ) -> featurestore_v1_entity_validation_service_pb2.CheckEntityEligibilityResponse:
        """Checks an entity."""
        deps = self.deps
        response = featurestore_v1_entity_validation_service_pb2.CheckEntityEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckEntityEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CheckEntityEligibility', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = patients_v1_patient_calculation_service_pb2.CalculatePatientResponse()
            response_1 = metrics_v1_metric_series_service_pb2.CreateMetricSeriesResponse()
            response_2 = audit_v1_audit_event_validation_service_pb2.CheckAuditEventEligibilityResponse()
            response_3 = featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewResponse()
            outgoing_0 = patients_v1_patient_calculation_service_pb2.CalculatePatientRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.entity.WhichOneof('identity_document') == 'passport':
                outgoing_0.patient.passport.number = request.entity.passport.number
            outgoing_0.patient.preferences.quiet_hours.CopyFrom(request.entity.preferences.quiet_hours)
            outgoing_0.details.destination.locality = request.entity.primary_address.locality
            if request.entity.WhichOneof('identity_document') == 'passport':
                outgoing_0.patient.passport.issuing_country = request.entity.passport.issuing_country
            response_0 = await deps.clients.patients_patient_calculation.CalculatePatient(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_series_service_pb2.CreateMetricSeriesRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.metric_series.audit.created_by = response_0.patient.audit.created_by
            outgoing_1.metric_series.audit.updated_by = response_0.patient.audit.updated_by
            outgoing_1.metric_series.owner.email = request.entity.contact.email
            merged_1 = metrics_v1_metric_series_service_pb2.CreateMetricSeriesRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.metrics_metric_series.CreateMetricSeries(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = audit_v1_audit_event_validation_service_pb2.CheckAuditEventEligibilityRequest(
                audit_event=audit_v1_audit_pb2.AuditEvent(
                    subject=audit_v1_refs_pb2.AuditTrailRef(number=response_0.patient.passport.number)
                ),
                context=request.context
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = audit_v1_audit_event_validation_service_pb2.CheckAuditEventEligibilityRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.audit_audit_event_validation.CheckAuditEventEligibility(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=response_0.patient.audit.created_at,
                        etag=response_0.patient.audit.etag
                    ),
                    components={
                        'primary': featurestore_v1_featurestore_pb2.FeatureViewComponent(
                            description=response_1.metric_series.components.get(
                                'primary',
                                metrics_v1_metrics_pb2.MetricSeriesComponent()
                            ).description
                        )
                    },
                    dimensions=featurestore_v1_featurestore_pb2.FeatureViewDimensions(
                        height=response_1.metric_series.dimensions.height
                    )
                )
            )
            registered_3 = cast(
                featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub,
                deps.clients.registry['acme.featurestore.v1.FeatureViewValidationService']
            )
            response_3 = await registered_3.PreviewFeatureView(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.patient.preferences.channels
            response.entity.preferences.channels.extend(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.metric_series.audit.etag
            if returned_1_0:
                response.entity.audit.etag = returned_1_0
            returned_2_0 = response_2.outcome.reference_id
            if returned_2_0:
                response.outcome.reference_id = returned_2_0
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.name
            response.entity.contact.name.CopyFrom(echoed_1)
            return response

    async def handle_explain_entity_decision(
        self,
        request: featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionRequest
    ) -> featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionResponse:
        """Explains an entity."""
        deps = self.deps
        response = featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainEntityDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExplainEntityDecision', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse()
            response_1 = featurestore_v1_entity_calculation_service_pb2.QuoteEntityResponse()
            command_0 = EntityValidationExplainEntityDecision0Command(
                context=request.context,
                details_destination_recipient=request.entity.primary_address.recipient,
                details_destination_country_code=request.entity.primary_address.country_code,
                details_destination_lines=list(request.entity.primary_address.lines)
            )
            outgoing_0 = to_entity_validation_explain_entity_decision0_command(command_0)
            response_0 = await deps.clients.featurestore_feature_value_calculation.RecalculateFeatureValues(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = EntityValidationExplainEntityDecision1Command.model_validate(
                {'context': request.context, 'entity_primary_address_region': request.entity.primary_address.region}
            )
            outgoing_1 = to_entity_validation_explain_entity_decision1_command(command_1)
            response_1 = await deps.clients.featurestore_entity_calculation.QuoteEntity(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.entity.audit.etag
            if returned_1_0:
                response.entity.audit.etag = returned_1_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.name
            response.entity.contact.name.CopyFrom(echoed_1)
            return response

    async def handle_get_entity_rules(
        self,
        request: featurestore_v1_entity_validation_service_pb2.GetEntityRulesRequest
    ) -> featurestore_v1_entity_validation_service_pb2.GetEntityRulesResponse:
        """Returns an entity."""
        deps = self.deps
        response = featurestore_v1_entity_validation_service_pb2.GetEntityRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetEntityRules', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(request.context.tenant_id, 'GetEntityRules', {'locale': request.context.locale})
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            return response

    async def handle_lint_entities(
        self,
        request: featurestore_v1_entity_validation_service_pb2.LintEntitiesRequest
    ) -> featurestore_v1_entity_validation_service_pb2.LintEntitiesResponse:
        """Lints an entity."""
        deps = self.deps
        response = featurestore_v1_entity_validation_service_pb2.LintEntitiesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintEntities', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintEntities', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksResponse()
            response_1 = featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityResponse()
            response_2 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksRequest(
                context=request.context,
                details=anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.entity.relationship_manager.email,
                        phone=request.details.contact.phone,
                        preferred_channel=request.entity.contact.preferred_channel
                    ),
                    strict=request.details.strict
                )
            )
            outgoing_1 = featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityRequest(
                context=request.context,
                details=featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.entity.audit.created_by),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.entity.relationship_manager.display_name)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.anomalies_anomaly_feedback_validation.LintAnomalyFeedbacks(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_feature_view_validation.CheckFeatureViewEligibility(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.filter.region = response_1.feature_view.address.region
            outgoing_2.filter.created_after.CopyFrom(request.entity.audit.created_at)
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.metrics_metric_alert_query.BrowseMetricAlerts(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.feature_view.address.lines
            response.entity.primary_address.lines.extend(returned_1_0)
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.attributes
            response.entity.attributes.update(echoed_1)
            return response

    async def handle_normalize_entity(
        self,
        request: featurestore_v1_entity_validation_service_pb2.NormalizeEntityRequest
    ) -> featurestore_v1_entity_validation_service_pb2.NormalizeEntityResponse:
        """Normalizes an entity."""
        deps = self.deps
        response = featurestore_v1_entity_validation_service_pb2.NormalizeEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse()
            response_1 = anomalies_v1_anomaly_service_pb2.CreateAnomalyResponse()
            response_2 = metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionResponse()
            outgoing_0 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(
                        locality=request.entity.primary_address.locality,
                        region=request.entity.primary_address.region
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.entity.audit.created_at)
                )
            )
            port_0: EntityValidationNormalizeEntity0Port = EntityValidationNormalizeEntity0Adapter(
                deps.clients.metrics_metric_series_export,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = anomalies_v1_anomaly_service_pb2.CreateAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    requester=common_v1_contact_pb2.ContactInfo(name=request.entity.contact.name)
                ),
                context=request.context
            )
            steps_1 = [partial(deps.clients.anomalies_anomaly.CreateAnomaly, outgoing_1, timeout=deps.settings.timeout)]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(lines=list(request.entity.primary_address.lines))
                )
            )
            response_2 = await EntityValidationNormalizeEntity2Adapter(
                deps.clients.metrics_metric_series_history,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.metric_series.audit.created_by
            if returned_0_1:
                response.entity.audit.created_by = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.anomaly.requester.name
            if returned_1_1.ListFields():
                response.entity.name.MergeFrom(returned_1_1)
            returned_2_0 = response_2.metric_series.audit.updated_by
            if returned_2_0:
                response.entity.audit.updated_by = returned_2_0
            returned_2_1 = response_2.metric_series.address.lines
            response.entity.primary_address.lines.extend(returned_2_1)
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.status
            response.entity.status = echoed_1
            return response

    async def handle_preview_entity(
        self,
        request: featurestore_v1_entity_validation_service_pb2.PreviewEntityRequest
    ) -> featurestore_v1_entity_validation_service_pb2.PreviewEntityResponse:
        """Previews an entity."""
        deps = self.deps
        response = featurestore_v1_entity_validation_service_pb2.PreviewEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewResponse()
            response_1 = featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueResponse()
            response_2 = lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityResponse()
            outgoing_0 = featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(recipient=request.entity.primary_address.recipient),
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.entity.audit.etag,
                        updated_at=request.entity.audit.updated_at
                    )
                )
            )
            response_0 = cast(featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewResponse, await deps.bus.request(
                'acme.featurestore.v1.EntityValidationService/PreviewEntity/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        postal_code=request.entity.primary_address.postal_code,
                        recipient=response_0.feature_view.address.recipient
                    )
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    subject=datasets_v1_refs_pb2.DatasetRef(
                        display_name=request.entity.relationship_manager.display_name
                    )
                )
            )
            response_1 = await deps.clients.featurestore_feature_value_calculation.CalculateFeatureValue(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(
                        display_name=request.entity.relationship_manager.display_name
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.entity.audit.created_by)
                )
            )
            method_name_2 = 'CheckImpactEligibility'
            response_2 = await getattr(
                deps.clients.lineage_impact_validation,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.feature_view.owner.display_name
            if returned_0_0:
                response.entity.relationship_manager.display_name = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.outcome.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.attributes
            response.entity.attributes.update(echoed_1)
            return response

    async def handle_score_entity(
        self,
        request: featurestore_v1_entity_validation_service_pb2.ScoreEntityRequest
    ) -> featurestore_v1_entity_validation_service_pb2.ScoreEntityResponse:
        """Scores an entity."""
        deps = self.deps
        response = featurestore_v1_entity_validation_service_pb2.ScoreEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = authorization_v1_access_policy_validation_service_pb2.LintAccessPoliciesResponse()
            fields_0: dict[str, Any] = {
                'access_policy': {'audit': {'updated_by': request.entity.audit.updated_by}},
                'context': request.context
            }
            outgoing_0 = authorization_v1_access_policy_validation_service_pb2.LintAccessPoliciesRequest(**fields_0)
            response_0 = await deps.clients.authorization_access_policy_validation.LintAccessPolicies(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.name
            response.entity.name.CopyFrom(echoed_1)
            return response

    async def handle_validate_entity(
        self,
        request: featurestore_v1_entity_validation_service_pb2.ValidateEntityRequest
    ) -> featurestore_v1_entity_validation_service_pb2.ValidateEntityResponse:
        """Validates an entity."""
        deps = self.deps
        response = featurestore_v1_entity_validation_service_pb2.ValidateEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksResponse()
            response_1 = featurestore_v1_entity_calculation_service_pb2.CalculateEntityResponse()
            response_2 = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardResponse()
            response_3 = lineage_v1_impact_validation_service_pb2.NormalizeImpactResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(
                        display_name=request.entity.relationship_manager.display_name
                    )
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.entity.contact.email,
                        name=request.details.contact.name,
                        phone=request.entity.contact.phone
                    )
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksRequest()
            )
            response_0 = await deps.clients.anomalies_anomaly_feedback_validation.LintAnomalyFeedbacks(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.entity.audit.etag),
                    relationship_manager=identity_v1_refs_pb2.UserRef(email=request.entity.contact.email)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest())
            response_1 = await deps.clients.featurestore_entity_calculation.CalculateEntity(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.dashboard.billing_address.country_code = request.entity.primary_address.country_code
            outgoing_2.dashboard.audit.updated_by = request.entity.audit.updated_by
            merged_2 = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.metrics_dashboard_validation.PreviewDashboard(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest(
                context=request.context,
                details=lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        phone=request.details.contact.phone,
                        preferred_channel=request.details.contact.preferred_channel
                    )
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.entity.contact.email)
                )
            )
            envelope_3 = AnyMessage()
            envelope_3.Pack(outgoing_3)
            outgoing_3 = lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest()
            if not envelope_3.Unpack(outgoing_3):
                raise ValueError("partner envelope contains the wrong request type")
            response_3 = await deps.clients.lineage_impact_validation.NormalizeImpact(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_1)
            returned_1_0 = response_1.entity.preferences.marketing_opt_in
            if returned_1_0:
                response.entity.preferences.marketing_opt_in = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.result.status = returned_3_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.name
            response.entity.contact.name.CopyFrom(echoed_1)
            return response
