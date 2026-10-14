"""Checks feature values against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.anomalies.v1 import refs_pb2 as anomalies_v1_refs_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.documents.v1 import documents_pb2 as documents_v1_documents_pb2
from acme.documents.v1 import refs_pb2 as documents_v1_refs_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2_grpc as featurestore_v1_feature_value_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.keymanagement.v1 import (
    crypto_key_calculation_service_pb2 as keymanagement_v1_crypto_key_calculation_service_pb2,
)
from acme.keymanagement.v1 import keymanagement_pb2 as keymanagement_v1_keymanagement_pb2
from acme.keymanagement.v1 import refs_pb2 as keymanagement_v1_refs_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.domains.featurestore.adapters import FeatureValueValidationNormalizeFeatureValue1Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureValueValidationValidateFeatureValue3Command
from acme_data.domains.featurestore.models import to_feature_value_validation_validate_feature_value3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FeatureValueValidationServicer(
    featurestore_v1_feature_value_validation_service_pb2_grpc.FeatureValueValidationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ExplainFeatureValueDecision(
        self, request: featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionResponse:
        """Explains a feature value."""
        return await self.handle_explain_feature_value_decision(request)

    @rpc_errors
    @retry_transient
    async def GetFeatureValueRules(
        self, request: featurestore_v1_feature_value_validation_service_pb2.GetFeatureValueRulesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_validation_service_pb2.GetFeatureValueRulesResponse:
        """Returns a feature value."""
        return await self.handle_get_feature_value_rules(request)

    @rpc_errors
    async def LintFeatureValues(
        self, request: featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesResponse:
        """Lints a feature value."""
        return await self.handle_lint_feature_values(request)

    @rpc_errors
    async def NormalizeFeatureValue(
        self, request: featurestore_v1_feature_value_validation_service_pb2.NormalizeFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_validation_service_pb2.NormalizeFeatureValueResponse:
        """Normalizes a feature value."""
        return await self.handle_normalize_feature_value(request)

    @rpc_errors
    async def PreviewFeatureValue(
        self, request: featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueResponse:
        """Previews a feature value."""
        return await self.handle_preview_feature_value(request)

    @rpc_errors
    async def ScoreFeatureValue(
        self, request: featurestore_v1_feature_value_validation_service_pb2.ScoreFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_validation_service_pb2.ScoreFeatureValueResponse:
        """Scores a feature value."""
        return await self.handle_score_feature_value(request)

    @rpc_errors
    async def ValidateFeatureValue(
        self, request: featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueResponse:
        """Validates a feature value."""
        return await self.handle_validate_feature_value(request)

    async def handle_explain_feature_value_decision(
        self,
        request: featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionRequest
    ) -> featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionResponse:
        """Explains a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainFeatureValueDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainFeatureValueDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsResponse()
            response_1 = featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsResponse()
            response_2 = lineage_v1_impact_validation_service_pb2.NormalizeImpactResponse()
            outgoing_0 = metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsRequest.Filter(
                    created_after=request.feature_value.occurred_at,
                    labels=dict(request.feature_value.attributes),
                    owner_id=request.feature_value.correlation_id
                )
            )
            outgoing_1 = featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    code=request.feature_value.subject.code,
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.feature_value.subject.display_name,
                        email=request.details.contact.email
                    )
                )
            )
            outgoing_2 = lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.feature_value.subject.display_name)
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.metrics_metric_alert_export.ListMetricAlertExports(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_feature_view_calculation.CompareFeatureViewOptions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.lineage_impact_validation.NormalizeImpact(outgoing_2, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.feature_view.owner.display_name
            if returned_1_1:
                response.feature_value.subject.display_name = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.correlation_id
            response.feature_value.correlation_id = echoed_1
            return response

    async def handle_get_feature_value_rules(
        self,
        request: featurestore_v1_feature_value_validation_service_pb2.GetFeatureValueRulesRequest
    ) -> featurestore_v1_feature_value_validation_service_pb2.GetFeatureValueRulesResponse:
        """Returns a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_validation_service_pb2.GetFeatureValueRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFeatureValueRules', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'GetFeatureValueRules', {})
            response_0 = venues_v1_venue_query_service_pb2.CountVenuesResponse()
            outgoing_0 = venues_v1_venue_query_service_pb2.CountVenuesRequest(
                context=request.context,
                filter=venues_v1_venue_query_service_pb2.CountVenuesRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.feature_value_id
                )
            )
            response_0 = await deps.clients.venues_venue_query.CountVenues(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            return response

    async def handle_lint_feature_values(
        self,
        request: featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesRequest
    ) -> featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesResponse:
        """Lints a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintFeatureValues', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintFeatureValues', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewResponse()
            response_1 = anomalies_v1_anomaly_service_pb2.BatchCreateAnomaliesResponse()
            outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.feature_view.owner.email = request.details.contact.email
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.featurestore_feature_view_calculation.SimulateFeatureView(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_service_pb2.BatchCreateAnomaliesRequest(
                context=request.context,
                record=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(email=response_0.feature_view.owner.email),
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.feature_view.audit.etag),
                    customer=anomalies_v1_refs_pb2.DetectorRef(display_name=response_0.feature_view.owner.display_name)
                )
            )
            response_1 = await deps.clients.anomalies_anomaly.BatchCreateAnomalies(
                async_messages((outgoing_1,)),
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_normalize_feature_value(
        self,
        request: featurestore_v1_feature_value_validation_service_pb2.NormalizeFeatureValueRequest
    ) -> featurestore_v1_feature_value_validation_service_pb2.NormalizeFeatureValueResponse:
        """Normalizes a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_validation_service_pb2.NormalizeFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_entity_calculation_service_pb2.QuoteEntityResponse()
            response_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackResponse()
            response_2 = featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueResponse()
            response_3 = keymanagement_v1_crypto_key_calculation_service_pb2.CompareCryptoKeyOptionsResponse()
            outgoing_0 = featurestore_v1_entity_calculation_service_pb2.QuoteEntityRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.featurestore_entity_calculation.QuoteEntity,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(
                        display_name=response_0.entity.relationship_manager.display_name
                    )
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.entity.primary_address.country_code,
                        recipient=response_0.entity.primary_address.recipient
                    )
                )
            )
            response_1 = await FeatureValueValidationNormalizeFeatureValue1Adapter(
                deps.clients.anomalies_anomaly_feedback_calculation,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        postal_code=response_0.entity.primary_address.postal_code
                    )
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    subject=datasets_v1_refs_pb2.DatasetRef(code=response_1.anomaly_feedback.subject.code)
                )
            )
            response_2 = cast(featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueResponse, await deps.bus.request(
                'acme.featurestore.v1.FeatureValueValidationService/NormalizeFeatureValue/2', outgoing_2, deps.settings.timeout,
            ))
            outgoing_3 = keymanagement_v1_crypto_key_calculation_service_pb2.CompareCryptoKeyOptionsRequest(
                context=request.context,
                crypto_key=keymanagement_v1_keymanagement_pb2.CryptoKey(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.entity.audit.created_by),
                    contact=common_v1_contact_pb2.ContactInfo(name=response_0.entity.contact.name),
                    holder=keymanagement_v1_refs_pb2.KeyRingRef(
                        display_name=response_1.anomaly_feedback.subject.display_name
                    )
                )
            )
            response_3 = await deps.clients.keymanagement_crypto_key_calculation.CompareCryptoKeyOptions(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.feature_value.correlation_id = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_preview_feature_value(
        self,
        request: featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueRequest
    ) -> featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueResponse:
        """Previews a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_entity_calculation_service_pb2.EstimateEntityResponse()
            response_1 = documents_v1_document_validation_service_pb2.LintDocumentsResponse()
            outgoing_0 = featurestore_v1_entity_calculation_service_pb2.EstimateEntityRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    attributes=dict(request.feature_value.attributes),
                    contact=common_v1_contact_pb2.ContactInfo(
                        phone=request.details.contact.phone,
                        preferred_channel=request.details.contact.preferred_channel
                    ),
                    name=request.details.contact.name
                )
            )
            method_name_0 = 'EstimateEntity'
            response_0 = await getattr(
                deps.clients.featurestore_entity_calculation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'document': {
                    'audit': {'updated_at': response_0.entity.audit.updated_at},
                    'billing_address': {
                        'lines': list(response_0.entity.primary_address.lines),
                        'postal_code': response_0.entity.primary_address.postal_code
                    },
                    'counterparty': {'display_name': response_0.entity.relationship_manager.display_name}
                }
            }
            outgoing_1 = documents_v1_document_validation_service_pb2.LintDocumentsRequest(**fields_1)
            response_1 = await deps.clients.documents_document_validation.LintDocuments(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.feature_value.correlation_id = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.source
            response.feature_value.source = echoed_1
            return response

    async def handle_score_feature_value(
        self,
        request: featurestore_v1_feature_value_validation_service_pb2.ScoreFeatureValueRequest
    ) -> featurestore_v1_feature_value_validation_service_pb2.ScoreFeatureValueResponse:
        """Scores a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_validation_service_pb2.ScoreFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesResponse()
            response_1 = documents_v1_document_validation_service_pb2.ValidateDocumentResponse()
            outgoing_0 = anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesRequest(
                context=request.context,
                filter=anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesRequest.Filter(
                    region=request.details.destination.region
                )
            )
            async for chunk_0 in deps.clients.anomalies_anomaly_query.ExportAnomalies(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = documents_v1_document_validation_service_pb2.ValidateDocumentRequest(
                context=request.context,
                document=documents_v1_documents_pb2.Document(
                    counterparty=documents_v1_refs_pb2.DocumentFolderRef(
                        display_name=request.feature_value.subject.display_name
                    ),
                    lines=[documents_v1_documents_pb2.DocumentLine(attributes=dict(request.feature_value.attributes))]
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, documents_v1_document_validation_service_pb2.ValidateDocumentRequest())
            response_1 = await deps.clients.documents_document_validation.ValidateDocument(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.document.total
            if returned_1_1.ListFields():
                response.breakdown.total.MergeFrom(returned_1_1)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.sequence
            response.feature_value.sequence = echoed_1
            return response

    async def handle_validate_feature_value(
        self,
        request: featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueRequest
    ) -> featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueResponse:
        """Validates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationResponse()
            response_1 = featurestore_v1_entity_calculation_service_pb2.CalculateEntityResponse()
            response_2 = featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewResponse()
            response_3 = anomalies_v1_detector_query_service_pb2.BrowseDetectorsResponse()
            outgoing_0 = featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.entity.contact.name.CopyFrom(request.details.contact.name)
            merged_0 = featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.featurestore_entity_calculation.ExplainEntityCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.entity.audit.updated_by),
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=response_0.entity.relationship_manager.display_name
                    )
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.featurestore_entity_calculation.CalculateEntity(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(region=response_1.entity.primary_address.region)
                )
            )
            registered_2 = cast(
                featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceStub,
                deps.clients.registry['acme.featurestore.v1.FeatureViewCalculationService']
            )
            response_2 = await registered_2.QuoteFeatureView(outgoing_2, timeout=deps.settings.timeout)
            command_3 = FeatureValueValidationValidateFeatureValue3Command(
                context=request.context,
                filter_region=response_1.entity.primary_address.region,
                filter_created_after=response_2.feature_view.audit.created_at,
                filter_owner_id=request.feature_value.subject.dataset_id,
                filter_labels=dict(response_1.result.details)
            )
            outgoing_3 = to_feature_value_validation_validate_feature_value3_command(command_3)
            response_3 = await deps.clients.anomalies_detector_query.BrowseDetectors(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.feature_value.correlation_id = returned_2_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.kind
            response.feature_value.kind = echoed_1
            return response
