"""Application workflow for RecommendationSet Query."""

from __future__ import annotations

import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2 as modelregistry_v1_model_version_validation_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2 as recommendations_v1_recommendation_set_query_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class RecommendationSetQueryServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_browse_recommendation_sets(
        self,
        request: recommendations_v1_recommendation_set_query_service_pb2.BrowseRecommendationSetsRequest
    ) -> recommendations_v1_recommendation_set_query_service_pb2.BrowseRecommendationSetsResponse:
        """Lists recommendation sets a page at a time."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_query_service_pb2.BrowseRecommendationSetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseRecommendationSets', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BrowseRecommendationSets',
                {'order_by': request.order_by}
            )
            return response

    async def handle_export_recommendation_sets(
        self,
        request: recommendations_v1_recommendation_set_query_service_pb2.ExportRecommendationSetsRequest
    ) -> recommendations_v1_recommendation_set_query_service_pb2.ExportRecommendationSetsResponse:
        """Streams every matching recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_query_service_pb2.ExportRecommendationSetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportRecommendationSets', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportRecommendationSets',
                {'destination_uri': request.destination_uri}
            )
            response_0 = recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse()
            response_1 = datasets_v1_dataset_validation_service_pb2.PreviewDatasetResponse()
            outgoing_0 = recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.recommendations_recommendation_model_validation.ExplainRecommendationModelDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_validation_service_pb2.PreviewDatasetRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.recommendation_model.audit.etag)
                )
            )
            method_name_1 = 'PreviewDataset'
            response_1 = await getattr(
                deps.clients.datasets_dataset_validation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.dataset.address.region
            if returned_1_0:
                response.recommendation_set.billing_address.region = returned_1_0
            return response

    async def handle_find_recommendation_sets(
        self,
        request: recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsRequest
    ) -> recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsResponse:
        """Lists recommendation sets a page at a time."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindRecommendationSets', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'FindRecommendationSets',
                {'order_by': request.order_by}
            )
            return response

    async def handle_lookup_recommendation_set(
        self,
        request: recommendations_v1_recommendation_set_query_service_pb2.LookupRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_query_service_pb2.LookupRecommendationSetResponse:
        """Returns a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_query_service_pb2.LookupRecommendationSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupRecommendationSet', extra={'fields': {'domain': 'recommendations'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupRecommendationSet', {})
            response_0 = recommendations_v1_interaction_validation_service_pb2.ValidateInteractionResponse()
            outgoing_0 = recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest(
                context=request.context,
                details=recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest.Details(
                    locale=request.context.locale
                ),
                interaction=recommendations_v1_recommendations_pb2.Interaction(
                    correlation_id=request.recommendation_set_id,
                    measurements=[
                        recommendations_v1_recommendations_pb2.InteractionMeasurement(
                            observed_at=request.context.deadline
                        )
                    ],
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.recommendations_interaction_validation.ValidateInteraction(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            return response

    async def handle_peek_recommendation_set(
        self,
        request: recommendations_v1_recommendation_set_query_service_pb2.PeekRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_query_service_pb2.PeekRecommendationSetResponse:
        """Returns a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_query_service_pb2.PeekRecommendationSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekRecommendationSet', extra={'fields': {'domain': 'recommendations'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekRecommendationSet', {})
            response_0 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionResponse()
            outgoing_0 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest(
                context=request.context,
                details=datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_validation.ExplainDatasetVersionDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            return response

    async def handle_suggest_recommendation_sets(
        self,
        request: recommendations_v1_recommendation_set_query_service_pb2.SuggestRecommendationSetsRequest
    ) -> recommendations_v1_recommendation_set_query_service_pb2.SuggestRecommendationSetsResponse:
        """Lists recommendation sets a page at a time."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_query_service_pb2.SuggestRecommendationSetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestRecommendationSets', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuggestRecommendationSets',
                {'order_by': request.order_by}
            )
            return response

    async def handle_summarize_recommendation_sets(
        self,
        request: recommendations_v1_recommendation_set_query_service_pb2.SummarizeRecommendationSetsRequest
    ) -> recommendations_v1_recommendation_set_query_service_pb2.SummarizeRecommendationSetsResponse:
        """Summarizes a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_query_service_pb2.SummarizeRecommendationSetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'SummarizeRecommendationSets',
                extra={'fields': {'recommendation_set_id': request.recommendation_set_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizeRecommendationSets',
                {'recommendation_set_id': request.recommendation_set_id}
            )
            response_0 = modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionResponse()
            response_1 = recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelResponse()
            outgoing_0 = modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionRequest()
            )
            response_0 = await deps.clients.modelregistry_model_version_validation.NormalizeModelVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.recommendation_model.owner.email = response_0.model_version.subject.email
            outgoing_1.recommendation_model.owner.display_name = response_0.model_version.subject.display_name
            merged_1 = recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.recommendations_recommendation_model_validation.ValidateRecommendationModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
