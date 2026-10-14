"""Application workflow for DatasetVersion Validation."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import anomaly_query_service_pb2_grpc as anomalies_v1_anomaly_query_service_pb2_grpc
from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.audit.v1 import audit_pb2 as audit_v1_audit_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2 as modelregistry_v1_model_version_validation_service_pb2,
)
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.shows.v1 import show_calculation_service_pb2 as shows_v1_show_calculation_service_pb2
from acme.shows.v1 import shows_pb2 as shows_v1_shows_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.domains.datasets import hooks
from acme_data.domains.datasets.adapters import DatasetVersionValidationNormalizeDatasetVersion0Adapter
from acme_data.domains.datasets.adapters import DatasetVersionValidationNormalizeDatasetVersion0Port
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.domains.datasets.models import DatasetVersionValidationExplainDatasetVersionDecision2Command
from acme_data.domains.datasets.models import to_dataset_version_validation_explain_dataset_version_decision2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DatasetVersionValidationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_check_dataset_version_eligibility(
        self,
        request: datasets_v1_dataset_version_validation_service_pb2.CheckDatasetVersionEligibilityRequest
    ) -> datasets_v1_dataset_version_validation_service_pb2.CheckDatasetVersionEligibilityResponse:
        """Checks a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_validation_service_pb2.CheckDatasetVersionEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckDatasetVersionEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckDatasetVersionEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityResponse()
            response_1 = labeling_v1_annotation_validation_service_pb2.PreviewAnnotationResponse()
            outgoing_0 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.contact.email,
                        phone=request.details.contact.phone,
                        preferred_channel=request.details.contact.preferred_channel
                    )
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest()
            )
            response_0 = await deps.clients.modelregistry_model_version_validation.CheckModelVersionEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_annotation_validation_service_pb2.PreviewAnnotationRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.contact.phone = request.details.contact.phone
            outgoing_1.details.contact.email = request.details.contact.email
            outgoing_1.annotation.subject.display_name = request.dataset_version.subject.display_name
            outgoing_1.annotation.kind = response_0.model_version.kind
            merged_1 = labeling_v1_annotation_validation_service_pb2.PreviewAnnotationRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.labeling_annotation_validation.PreviewAnnotation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.annotation.subject.display_name
            if returned_1_0:
                response.dataset_version.subject.display_name = returned_1_0
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.kind
            response.dataset_version.kind = echoed_1
            return response

    async def handle_explain_dataset_version_decision(
        self,
        request: datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest
    ) -> datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionResponse:
        """Explains a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'ExplainDatasetVersionDecision',
                extra={'fields': {'dataset_version_id': request.dataset_version.dataset_version_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainDatasetVersionDecision',
                {'dataset_version_id': request.dataset_version.dataset_version_id}
            )
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = audit_v1_audit_event_validation_service_pb2.ScoreAuditEventResponse()
            response_1 = anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesResponse()
            response_2 = identity_v1_user_query_service_pb2.BrowseUsersResponse()
            callbacks_0: list[
                Callable[[], Awaitable[audit_v1_audit_event_validation_service_pb2.ScoreAuditEventResponse]]
            ] = []
            for item_0 in request.dataset_version.measurements:
                outgoing_0 = audit_v1_audit_event_validation_service_pb2.ScoreAuditEventRequest(
                    audit_event=audit_v1_audit_pb2.AuditEvent(
                        measurements=[
                            audit_v1_audit_pb2.AuditEventMeasurement(observed_at=item_0.observed_at, value=item_0.value)
                        ]
                    ),
                    context=request.context
                )
                async def send_0(
                    payload: audit_v1_audit_event_validation_service_pb2.ScoreAuditEventRequest = outgoing_0
                ) -> audit_v1_audit_event_validation_service_pb2.ScoreAuditEventResponse:
                    return await deps.clients.audit_audit_event_validation.ScoreAuditEvent(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            outgoing_1 = anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesRequest.Details(
                    filters=dict(request.dataset_version.attributes)
                ),
                reason=request.reason
            )
            registered_1 = cast(
                anomalies_v1_anomaly_query_service_pb2_grpc.AnomalyQueryServiceStub,
                deps.clients.registry['acme.anomalies.v1.AnomalyQueryService']
            )
            response_1 = await registered_1.SummarizeAnomalies(outgoing_1, timeout=deps.settings.timeout)
            command_2 = DatasetVersionValidationExplainDatasetVersionDecision2Command(
                context=request.context,
                filter_created_after=response_0.audit_event.occurred_at
            )
            outgoing_2 = to_dataset_version_validation_explain_dataset_version_decision2_command(command_2)
            response_2 = await deps.clients.identity_user_query.BrowseUsers(outgoing_2, timeout=deps.settings.timeout)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.correlation_id
            response.dataset_version.correlation_id = echoed_1
            return response

    async def handle_get_dataset_version_rules(
        self,
        request: datasets_v1_dataset_version_validation_service_pb2.GetDatasetVersionRulesRequest
    ) -> datasets_v1_dataset_version_validation_service_pb2.GetDatasetVersionRulesResponse:
        """Returns a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_validation_service_pb2.GetDatasetVersionRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDatasetVersionRules', extra={'fields': {'domain': 'datasets'}})
            await deps.repository.audit(request.context.tenant_id, 'GetDatasetVersionRules', {})
            response_0 = shows_v1_show_calculation_service_pb2.EstimateShowResponse()
            response_1 = labeling_v1_annotation_validation_service_pb2.LintAnnotationsResponse()
            outgoing_0 = shows_v1_show_calculation_service_pb2.EstimateShowRequest(
                context=request.context,
                show=shows_v1_shows_pb2.Show(
                    organizer=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    participants=[
                        shows_v1_shows_pb2.ShowParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                        )
                    ]
                )
            )
            response_0 = await deps.clients.shows_show_calculation.EstimateShow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_annotation_validation_service_pb2.LintAnnotationsRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(display_name=response_0.show.organizer.display_name)
                ),
                context=request.context
            )
            send_1 = partial(deps.clients.labeling_annotation_validation.LintAnnotations, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.show.organizer.display_name
            if returned_0_0:
                response.dataset_version.subject.display_name = returned_0_0
            returned_1_0 = response_1.annotation.source
            if returned_1_0:
                response.dataset_version.source = returned_1_0
            returned_1_1 = response_1.annotation.attributes
            response.dataset_version.attributes.update(returned_1_1)
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            return response

    async def handle_lint_dataset_versions(
        self,
        request: datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsRequest
    ) -> datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsResponse:
        """Lints a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintDatasetVersions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintDatasetVersions', {'reason': request.reason})
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionResponse()
            response_1 = featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.details.contact.email)
                )
            )
            response_0 = await hooks.dataset_version_validation_lint_dataset_versions0(
                deps.clients.datasets_dataset_version_calculation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.feature_view.owner.display_name = response_0.dataset_version.subject.display_name
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.featurestore_feature_view_validation.ValidateFeatureView(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset_version.sequence
            if returned_0_0:
                response.dataset_version.sequence = returned_0_0
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.attributes
            response.dataset_version.attributes.update(echoed_1)
            return response

    async def handle_normalize_dataset_version(
        self,
        request: datasets_v1_dataset_version_validation_service_pb2.NormalizeDatasetVersionRequest
    ) -> datasets_v1_dataset_version_validation_service_pb2.NormalizeDatasetVersionResponse:
        """Normalizes a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_validation_service_pb2.NormalizeDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeDatasetVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'NormalizeDatasetVersion',
                {'reason': request.reason}
            )
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaResponse()
            outgoing_0 = datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    manager=identity_v1_refs_pb2.UserRef(email=request.dataset_version.subject.email)
                                )
                            ]
                        )
                    ],
                    manager=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                )
            )
            port_0: DatasetVersionValidationNormalizeDatasetVersion0Port = DatasetVersionValidationNormalizeDatasetVersion0Adapter(
                deps.clients.datasets_data_schema_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            returned_0_0 = response_0.data_schema.manager.display_name
            if returned_0_0:
                response.dataset_version.subject.display_name = returned_0_0
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.correlation_id
            response.dataset_version.correlation_id = echoed_1
            return response

    async def handle_preview_dataset_version(
        self,
        request: datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionRequest
    ) -> datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionResponse:
        """Previews a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewDatasetVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewDatasetVersion', {'reason': request.reason})
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaResponse()
            response_1 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionResponse()
            response_2 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationResponse()
            outgoing_0 = datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.dataset_version.subject.display_name,
                                        email=request.dataset_version.subject.email
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                        )
                    ]
                )
            )
            steps_0 = [
                partial(
                    deps.clients.datasets_data_schema_calculation.CalculateDataSchema,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            async for item_1 in async_messages(request.dataset_version.measurements):
                outgoing_1 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest(
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
                response_1 = await deps.clients.datasets_dataset_version_calculation.EstimateDatasetVersion(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        customer_id=response_1.dataset_version.subject.customer_id
                    )
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
                )
            )
            response_2 = cast(datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationResponse, await deps.bus.request(
                'acme.datasets.v1.DatasetVersionValidationService/PreviewDatasetVersion/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_1)
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.subject
            response.dataset_version.subject.CopyFrom(echoed_1)
            return response

    async def handle_score_dataset_version(
        self,
        request: datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionRequest
    ) -> datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionResponse:
        """Scores a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreDatasetVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreDatasetVersion', {'reason': request.reason})
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasResponse()
            response_1 = datasets_v1_data_schema_calculation_service_pb2.ExplainDataSchemaCalculationResponse()
            response_2 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityResponse()
            response_3 = pipelines_v1_pipeline_query_service_pb2.FindPipelinesResponse()
            outgoing_0 = datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    location=common_v1_address_pb2.PostalAddress(
                                        locality=request.details.destination.locality
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_0 = await deps.clients.datasets_data_schema_calculation.RecalculateDataSchemas(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_data_schema_calculation_service_pb2.ExplainDataSchemaCalculationRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        updated_by=response_0.data_schema.audit.updated_by
                                    ),
                                    location=common_v1_address_pb2.PostalAddress(
                                        postal_code=response_0.data_schema.location.postal_code,
                                        recipient=response_0.data_schema.location.recipient
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.data_schema.manager.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            method_name_1 = 'ExplainDataSchemaCalculation'
            response_1 = await getattr(
                deps.clients.datasets_data_schema_calculation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {
                'context': request.context,
                'details': {'contact': {'email': request.dataset_version.subject.email}},
                'model_version': {
                    'subject': {
                        'display_name': request.dataset_version.subject.display_name,
                        'email': response_0.data_schema.manager.email
                    }
                }
            }
            outgoing_2 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest(**fields_2)
            response_2 = await deps.clients.modelregistry_model_version_validation.CheckModelVersionEligibility(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = pipelines_v1_pipeline_query_service_pb2.FindPipelinesRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_query_service_pb2.FindPipelinesRequest.Filter(
                    created_after=response_1.data_schema.audit.created_at,
                    labels=dict(response_2.result.details),
                    owner_id=response_1.data_schema.manager.user_id,
                    region=response_1.data_schema.location.region
                )
            )
            document_3 = MessageToDict(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = ParseDict(document_3, pipelines_v1_pipeline_query_service_pb2.FindPipelinesRequest())
            response_3 = await deps.clients.pipelines_pipeline_query.FindPipelines(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.dataset_version.correlation_id = returned_3_0
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.subject
            response.dataset_version.subject.CopyFrom(echoed_1)
            return response

    async def handle_validate_dataset_version(
        self,
        request: datasets_v1_dataset_version_validation_service_pb2.ValidateDatasetVersionRequest
    ) -> datasets_v1_dataset_version_validation_service_pb2.ValidateDatasetVersionResponse:
        """Validates a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_validation_service_pb2.ValidateDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateDatasetVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateDatasetVersion', {'reason': request.reason})
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = documents_v1_document_query_service_pb2.ExportDocumentsResponse()
            response_1 = venues_v1_venue_query_service_pb2.BrowseVenuesResponse()
            outgoing_0 = documents_v1_document_query_service_pb2.ExportDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_query_service_pb2.ExportDocumentsRequest.Filter(
                    created_after=request.dataset_version.occurred_at,
                    labels=dict(request.dataset_version.attributes),
                    owner_id=request.dataset_version.subject.customer_id
                )
            )
            async for chunk_0 in deps.clients.documents_document_query.ExportDocuments(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            for item_1 in request.dataset_version.measurements:
                outgoing_1 = venues_v1_venue_query_service_pb2.BrowseVenuesRequest(
                    context=request.context,
                    filter=venues_v1_venue_query_service_pb2.BrowseVenuesRequest.Filter(
                        created_after=item_1.observed_at,
                        labels=dict(request.annotations),
                        owner_id=request.dataset_version.correlation_id
                    )
                )
                response_1 = await deps.clients.venues_venue_query.BrowseVenues(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.correlation_id
            response.result.correlation_id = echoed_1
            return response
