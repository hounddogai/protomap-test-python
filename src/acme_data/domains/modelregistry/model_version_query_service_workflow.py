"""Application workflow for ModelVersion Query."""

from __future__ import annotations

from functools import partial
import asyncio
import logging

from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.certificates.v1 import (
    certificate_calculation_service_pb2 as certificates_v1_certificate_calculation_service_pb2,
)
from acme.certificates.v1 import certificates_pb2 as certificates_v1_certificates_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import model_version_query_service_pb2 as modelregistry_v1_model_version_query_service_pb2
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2 as modelregistry_v1_model_version_validation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.ticketing.v1 import ticket_service_pb2 as ticketing_v1_ticket_service_pb2

from acme_data.domains.modelregistry.adapters import ModelVersionQueryPeekModelVersion1Adapter
from acme_data.domains.modelregistry.adapters import ModelVersionQueryPeekModelVersion1Port
from acme_data.domains.modelregistry.adapters import ModelVersionQuerySummarizeModelVersions1Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ModelVersionQueryServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_browse_model_versions(
        self,
        request: modelregistry_v1_model_version_query_service_pb2.BrowseModelVersionsRequest
    ) -> modelregistry_v1_model_version_query_service_pb2.BrowseModelVersionsResponse:
        """Lists model versions a page at a time."""
        deps = self.deps
        response = modelregistry_v1_model_version_query_service_pb2.BrowseModelVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseModelVersions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BrowseModelVersions',
                {'order_by': request.order_by}
            )
            response_0 = ticketing_v1_ticket_service_pb2.BatchGetTicketsResponse()
            outgoing_0 = ticketing_v1_ticket_service_pb2.BatchGetTicketsRequest(context=request.context)
            response_0 = await deps.clients.ticketing_ticket.BatchGetTickets(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            return response

    async def handle_count_model_versions(
        self,
        request: modelregistry_v1_model_version_query_service_pb2.CountModelVersionsRequest
    ) -> modelregistry_v1_model_version_query_service_pb2.CountModelVersionsResponse:
        """Counts model versions by status."""
        deps = self.deps
        response = modelregistry_v1_model_version_query_service_pb2.CountModelVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountModelVersions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountModelVersions', {'order_by': request.order_by})
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelResponse()
            outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelRequest(
                context=request.context,
                details=modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.modelregistry_registered_model_calculation.CalculateRegisteredModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            return response

    async def handle_export_model_versions(
        self,
        request: modelregistry_v1_model_version_query_service_pb2.ExportModelVersionsRequest
    ) -> modelregistry_v1_model_version_query_service_pb2.ExportModelVersionsResponse:
        """Streams every matching model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_query_service_pb2.ExportModelVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportModelVersions', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportModelVersions',
                {'destination_uri': request.destination_uri}
            )
            response_0 = certificates_v1_certificate_calculation_service_pb2.ExplainCertificateCalculationResponse()
            response_1 = modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsResponse()
            response_2 = audit_v1_audit_event_service_pb2.BatchGetAuditEventsResponse()
            outgoing_0 = certificates_v1_certificate_calculation_service_pb2.ExplainCertificateCalculationRequest(
                certificate=certificates_v1_certificates_pb2.Certificate(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                context=request.context
            )
            outgoing_2 = audit_v1_audit_event_service_pb2.BatchGetAuditEventsRequest(context=request.context)
            response_0, response_2 = await asyncio.gather(
                deps.clients.certificates_certificate_calculation.ExplainCertificateCalculation(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.audit_audit_event.BatchGetAuditEvents(outgoing_2, timeout=deps.settings.timeout),
            )
            outgoing_1 = modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=response_0.certificate.counterparty.display_name
                    )
                )
            )
            send_1 = partial(
                deps.clients.modelregistry_model_version_validation.LintModelVersions,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.model_version.correlation_id = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.model_version.subject.email
            if returned_1_0:
                response.model_version.subject.email = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.model_version.correlation_id = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            return response

    async def handle_lookup_model_version(
        self,
        request: modelregistry_v1_model_version_query_service_pb2.LookupModelVersionRequest
    ) -> modelregistry_v1_model_version_query_service_pb2.LookupModelVersionResponse:
        """Returns a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_query_service_pb2.LookupModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupModelVersion', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'LookupModelVersion',
                {'locale': request.context.locale}
            )
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            return response

    async def handle_peek_model_version(
        self,
        request: modelregistry_v1_model_version_query_service_pb2.PeekModelVersionRequest
    ) -> modelregistry_v1_model_version_query_service_pb2.PeekModelVersionResponse:
        """Returns a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_query_service_pb2.PeekModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekModelVersion', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekModelVersion', {})
            response_0 = modelregistry_v1_model_version_calculation_service_pb2.QuoteModelVersionResponse()
            response_1 = featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewResponse()
            outgoing_0 = modelregistry_v1_model_version_calculation_service_pb2.QuoteModelVersionRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.modelregistry_model_version_calculation.QuoteModelVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.model_version.subject.display_name)
                )
            )
            port_1: ModelVersionQueryPeekModelVersion1Port = ModelVersionQueryPeekModelVersion1Adapter(
                deps.clients.featurestore_feature_view_calculation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.model_version.subject.display_name
            if returned_0_0:
                response.model_version.subject.display_name = returned_0_0
            returned_1_0 = response_1.feature_view.owner.display_name
            if returned_1_0:
                response.model_version.subject.display_name = returned_1_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            return response

    async def handle_suggest_model_versions(
        self,
        request: modelregistry_v1_model_version_query_service_pb2.SuggestModelVersionsRequest
    ) -> modelregistry_v1_model_version_query_service_pb2.SuggestModelVersionsResponse:
        """Lists model versions a page at a time."""
        deps = self.deps
        response = modelregistry_v1_model_version_query_service_pb2.SuggestModelVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestModelVersions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuggestModelVersions',
                {'order_by': request.order_by}
            )
            return response

    async def handle_summarize_model_versions(
        self,
        request: modelregistry_v1_model_version_query_service_pb2.SummarizeModelVersionsRequest
    ) -> modelregistry_v1_model_version_query_service_pb2.SummarizeModelVersionsResponse:
        """Summarizes a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_query_service_pb2.SummarizeModelVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeModelVersions', extra={'fields': {'model_version_id': request.model_version_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizeModelVersions',
                {'model_version_id': request.model_version_id}
            )
            response_0 = audit_v1_audit_event_service_pb2.WatchAuditEventsResponse()
            response_1 = modelregistry_v1_deployment_validation_service_pb2.NormalizeDeploymentResponse()
            outgoing_0 = audit_v1_audit_event_service_pb2.WatchAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_service_pb2.WatchAuditEventsRequest.Filter(
                    labels=dict(request.annotations),
                    owner_id=request.context.trace_id
                ),
                since=request.context.deadline,
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            )
            async for chunk_0 in deps.clients.audit_audit_event.WatchAuditEvents(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = modelregistry_v1_deployment_validation_service_pb2.NormalizeDeploymentRequest(
                annotations=dict(request.annotations),
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    organizer=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                        )
                    ]
                ),
                reason=request.reason
            )
            response_1 = await ModelVersionQuerySummarizeModelVersions1Adapter(
                deps.clients.modelregistry_deployment_validation,
                deps.settings.timeout
            )(outgoing_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
