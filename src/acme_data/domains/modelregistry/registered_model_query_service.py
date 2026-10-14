"""Answers read-only questions about registered models, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
import logging

import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.concessions.v1 import concession_stand_service_pb2 as concessions_v1_concession_stand_service_pb2
from acme.concessions.v1 import concessions_pb2 as concessions_v1_concessions_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_alert_admin_service_pb2 as metrics_v1_metric_alert_admin_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2_grpc as modelregistry_v1_registered_model_query_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class RegisteredModelQueryServicer(
    modelregistry_v1_registered_model_query_service_pb2_grpc.RegisteredModelQueryServiceServicer
):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def BrowseRegisteredModels(
        self, request: modelregistry_v1_registered_model_query_service_pb2.BrowseRegisteredModelsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_query_service_pb2.BrowseRegisteredModelsResponse:
        """Lists registered models a page at a time."""
        return await self.handle_browse_registered_models(request)

    @rpc_errors
    @retry_transient
    async def CountRegisteredModels(
        self, request: modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsResponse:
        """Counts registered models by status."""
        return await self.handle_count_registered_models(request)

    @rpc_errors
    @retry_transient
    async def FindRegisteredModels(
        self, request: modelregistry_v1_registered_model_query_service_pb2.FindRegisteredModelsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_query_service_pb2.FindRegisteredModelsResponse:
        """Lists registered models a page at a time."""
        return await self.handle_find_registered_models(request)

    @rpc_errors
    @retry_transient
    async def LookupRegisteredModel(
        self, request: modelregistry_v1_registered_model_query_service_pb2.LookupRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_query_service_pb2.LookupRegisteredModelResponse:
        """Returns a registered model."""
        return await self.handle_lookup_registered_model(request)

    @rpc_errors
    @retry_transient
    async def PeekRegisteredModel(
        self, request: modelregistry_v1_registered_model_query_service_pb2.PeekRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_query_service_pb2.PeekRegisteredModelResponse:
        """Returns a registered model."""
        return await self.handle_peek_registered_model(request)

    @rpc_errors
    @retry_transient
    async def ResolveRegisteredModels(
        self, request: modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsResponse:
        """Returns several registered models at once."""
        return await self.handle_resolve_registered_models(request)

    async def handle_browse_registered_models(
        self,
        request: modelregistry_v1_registered_model_query_service_pb2.BrowseRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_query_service_pb2.BrowseRegisteredModelsResponse:
        """Lists registered models a page at a time."""
        deps = self.deps
        response = modelregistry_v1_registered_model_query_service_pb2.BrowseRegisteredModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseRegisteredModels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BrowseRegisteredModels',
                {'order_by': request.order_by}
            )
            response_0 = modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentResponse()
            outgoing_0 = modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                        )
                    ]
                )
            )
            response_0 = await deps.clients.modelregistry_deployment_calculation.QuoteDeployment(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.deployment.audit.etag
            returned_0_1_part_0 = response.registered_models.add()
            if returned_0_1:
                returned_0_1_part_0.audit.etag = returned_0_1
            return response

    async def handle_count_registered_models(
        self,
        request: modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsResponse:
        """Counts registered models by status."""
        deps = self.deps
        response = modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountRegisteredModels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountRegisteredModels',
                {'order_by': request.order_by}
            )
            return response

    async def handle_find_registered_models(
        self,
        request: modelregistry_v1_registered_model_query_service_pb2.FindRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_query_service_pb2.FindRegisteredModelsResponse:
        """Lists registered models a page at a time."""
        deps = self.deps
        response = modelregistry_v1_registered_model_query_service_pb2.FindRegisteredModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindRegisteredModels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'FindRegisteredModels',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsResponse()
            outgoing_0 = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.metrics_metric_series_history.CompareMetricSeriesVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            return response

    async def handle_lookup_registered_model(
        self,
        request: modelregistry_v1_registered_model_query_service_pb2.LookupRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_query_service_pb2.LookupRegisteredModelResponse:
        """Returns a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_query_service_pb2.LookupRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupRegisteredModel', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupRegisteredModel', {})
            response_0 = modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentResponse()
            outgoing_0 = modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    organizer=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                ),
                details=modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentRequest.Details(
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.modelregistry_deployment_validation.PreviewDeployment(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.deployment.audit.created_by
            if returned_0_0:
                response.registered_model.audit.created_by = returned_0_0
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            return response

    async def handle_peek_registered_model(
        self,
        request: modelregistry_v1_registered_model_query_service_pb2.PeekRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_query_service_pb2.PeekRegisteredModelResponse:
        """Returns a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_query_service_pb2.PeekRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekRegisteredModel', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekRegisteredModel', {})
            response_0 = modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsResponse()
            outgoing_0 = modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    organizer=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.modelregistry_deployment_calculation.RecalculateDeployments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.deployment.organizer.display_name
            if returned_0_0:
                response.registered_model.owner.display_name = returned_0_0
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            return response

    async def handle_resolve_registered_models(
        self,
        request: modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsResponse:
        """Returns several registered models at once."""
        deps = self.deps
        response = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveRegisteredModels', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'ResolveRegisteredModels', {})
            response_0 = concessions_v1_concession_stand_service_pb2.CloneConcessionStandResponse()
            response_1 = metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertResponse()
            outgoing_0 = concessions_v1_concession_stand_service_pb2.CloneConcessionStandRequest(
                concession_stand=concessions_v1_concessions_pb2.ConcessionStand(
                    owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                ),
                context=request.context
            )
            response_0 = await deps.clients.concessions_concession_stand.CloneConcessionStand(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.metric_alert.owner.user_id = response_0.concession_stand.owner.user_id
            outgoing_1.metric_alert.owner.display_name = response_0.concession_stand.owner.display_name
            outgoing_1.metric_alert.audit.etag = response_0.concession_stand.audit.etag
            outgoing_1.metric_alert.description = response_0.concession_stand.components.get(
                'primary',
                concessions_v1_concessions_pb2.ConcessionStandComponent()
            ).description
            merged_1 = metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.metrics_metric_alert_admin.RepairMetricAlert(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.concession_stand.owner.email
            returned_0_0_part_0 = response.registered_models.add()
            if returned_0_0:
                returned_0_0_part_0.owner.email = returned_0_0
            returned_0_1 = response_0.concession_stand.name
            returned_0_1_part_0 = response.registered_models.add()
            if returned_0_1:
                returned_0_1_part_0.name = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            return response
