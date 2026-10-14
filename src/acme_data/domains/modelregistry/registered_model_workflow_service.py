"""Runs the long-lived workflow that takes a registered model from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import household_query_service_pb2 as customers_v1_household_query_service_pb2
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metric_series_admin_service_pb2 as metrics_v1_metric_series_admin_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import (
    model_version_approval_service_pb2 as modelregistry_v1_model_version_approval_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2_grpc as modelregistry_v1_registered_model_sync_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_workflow_service_pb2 as modelregistry_v1_registered_model_workflow_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_workflow_service_pb2_grpc as modelregistry_v1_registered_model_workflow_service_pb2_grpc,
)

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import RegisteredModelWorkflowAdvanceRegisteredModelWorkflow1Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import RegisteredModelWorkflowSignalRegisteredModelWorkflow3Command
from acme_data.domains.modelregistry.models import (
    to_registered_model_workflow_signal_registered_model_workflow3_command,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class RegisteredModelWorkflowServicer(
    modelregistry_v1_registered_model_workflow_service_pb2_grpc.RegisteredModelWorkflowServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def AdvanceRegisteredModelWorkflow(
        self, request: modelregistry_v1_registered_model_workflow_service_pb2.AdvanceRegisteredModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.AdvanceRegisteredModelWorkflowResponse:
        """Advances a registered model."""
        return await self.handle_advance_registered_model_workflow(request)

    @rpc_errors
    async def CancelRegisteredModelWorkflow(
        self, request: modelregistry_v1_registered_model_workflow_service_pb2.CancelRegisteredModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.CancelRegisteredModelWorkflowResponse:
        """Cancels a registered model."""
        return await self.handle_cancel_registered_model_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectRegisteredModelWorkflow(
        self, request: modelregistry_v1_registered_model_workflow_service_pb2.InspectRegisteredModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.InspectRegisteredModelWorkflowResponse:
        """Returns a registered model."""
        return await self.handle_inspect_registered_model_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListRegisteredModelWorkflows(
        self, request: modelregistry_v1_registered_model_workflow_service_pb2.ListRegisteredModelWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.ListRegisteredModelWorkflowsResponse:
        """Lists registered models a page at a time."""
        return await self.handle_list_registered_model_workflows(request)

    @rpc_errors
    async def ResumeRegisteredModelWorkflow(
        self, request: modelregistry_v1_registered_model_workflow_service_pb2.ResumeRegisteredModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.ResumeRegisteredModelWorkflowResponse:
        """Resumes a registered model."""
        return await self.handle_resume_registered_model_workflow(request)

    @rpc_errors
    async def RetryRegisteredModelWorkflow(
        self, request: modelregistry_v1_registered_model_workflow_service_pb2.RetryRegisteredModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.RetryRegisteredModelWorkflowResponse:
        """Retrys a registered model."""
        return await self.handle_retry_registered_model_workflow(request)

    @rpc_errors
    async def SignalRegisteredModelWorkflow(
        self, request: modelregistry_v1_registered_model_workflow_service_pb2.SignalRegisteredModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.SignalRegisteredModelWorkflowResponse:
        """Signals a registered model."""
        return await self.handle_signal_registered_model_workflow(request)

    @rpc_errors
    async def StartRegisteredModelWorkflow(
        self, request: modelregistry_v1_registered_model_workflow_service_pb2.StartRegisteredModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.StartRegisteredModelWorkflowResponse:
        """Starts a registered model."""
        return await self.handle_start_registered_model_workflow(request)

    async def handle_advance_registered_model_workflow(
        self,
        request: modelregistry_v1_registered_model_workflow_service_pb2.AdvanceRegisteredModelWorkflowRequest
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.AdvanceRegisteredModelWorkflowResponse:
        """Advances a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_workflow_service_pb2.AdvanceRegisteredModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceRegisteredModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceRegisteredModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = modelregistry_v1_deployment_calculation_service_pb2.EstimateDeploymentResponse()
            response_1 = ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsResponse()
            outgoing_0 = modelregistry_v1_deployment_calculation_service_pb2.EstimateDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                name=request.details.notify.name,
                                phone=request.details.notify.phone,
                                preferred_channel=request.details.notify.preferred_channel
                            )
                        )
                    ]
                )
            )
            steps_0 = [
                partial(
                    deps.clients.modelregistry_deployment_calculation.EstimateDeployment,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsRequest.Filter(
                    created_after=request.registered_model.audit.updated_at,
                    labels=dict(response_0.deployment.metadata),
                    owner_id=request.registered_model.owner.user_id,
                    region=request.registered_model.address.region
                )
            )
            response_1 = await RegisteredModelWorkflowAdvanceRegisteredModelWorkflow1Adapter(
                deps.clients.ledger_ledger_account_query,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.deployment.audit.etag
            if returned_0_1:
                response.registered_model.audit.etag = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.status
            response.registered_model.status = echoed_1
            return response

    async def handle_cancel_registered_model_workflow(
        self,
        request: modelregistry_v1_registered_model_workflow_service_pb2.CancelRegisteredModelWorkflowRequest
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.CancelRegisteredModelWorkflowResponse:
        """Cancels a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_workflow_service_pb2.CancelRegisteredModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelRegisteredModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelRegisteredModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardResponse()
            response_1 = modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportResponse()
            outgoing_0 = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.registered_model.audit.created_by,
                        updated_by=request.registered_model.audit.updated_by
                    )
                ),
                details=metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                )
            )
            response_0 = cast(metrics_v1_dashboard_validation_service_pb2.PreviewDashboardResponse, await deps.bus.request(
                'acme.modelregistry.v1.RegisteredModelWorkflowService/CancelRegisteredModelWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportRequest(
                context=request.context,
                details=modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify.email,
                        name=request.details.notify.name,
                        phone=request.details.notify.phone
                    )
                )
            )
            response_1 = await deps.clients.modelregistry_model_version_reporting.ShareModelVersionReport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.audit.created_at
            if returned_0_0.ListFields():
                response.registered_model.audit.created_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.outcome.effective_at
            if returned_1_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.capacity
            response.registered_model.capacity = echoed_1
            return response

    async def handle_inspect_registered_model_workflow(
        self,
        request: modelregistry_v1_registered_model_workflow_service_pb2.InspectRegisteredModelWorkflowRequest
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.InspectRegisteredModelWorkflowResponse:
        """Returns a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_workflow_service_pb2.InspectRegisteredModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectRegisteredModelWorkflow', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectRegisteredModelWorkflow',
                {'locale': request.context.locale}
            )
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            return response

    async def handle_list_registered_model_workflows(
        self,
        request: modelregistry_v1_registered_model_workflow_service_pb2.ListRegisteredModelWorkflowsRequest
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.ListRegisteredModelWorkflowsResponse:
        """Lists registered models a page at a time."""
        deps = self.deps
        response = modelregistry_v1_registered_model_workflow_service_pb2.ListRegisteredModelWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListRegisteredModelWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListRegisteredModelWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = customers_v1_household_query_service_pb2.CountHouseholdsResponse()
            response_1 = modelregistry_v1_deployment_sync_service_pb2.PushDeploymentResponse()
            outgoing_0 = customers_v1_household_query_service_pb2.CountHouseholdsRequest(
                context=request.context,
                page=common_v1_paging_pb2.PageRequest(page_token=request.page.page_token)
            )
            response_0 = await deps.clients.customers_household_query.CountHouseholds(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            fields_1: dict[str, Any] = {
                'context': request.context,
                'deployment': {'location': {'region': request.filter.region}}
            }
            outgoing_1 = modelregistry_v1_deployment_sync_service_pb2.PushDeploymentRequest(**fields_1)
            response_1 = await deps.clients.modelregistry_deployment_sync.PushDeployment(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.deployment.audit.updated_at
            returned_1_0_part_0 = response.registered_models.add()
            if returned_1_0.ListFields():
                returned_1_0_part_0.audit.updated_at.MergeFrom(returned_1_0)
            return response

    async def handle_resume_registered_model_workflow(
        self,
        request: modelregistry_v1_registered_model_workflow_service_pb2.ResumeRegisteredModelWorkflowRequest
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.ResumeRegisteredModelWorkflowResponse:
        """Resumes a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_workflow_service_pb2.ResumeRegisteredModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeRegisteredModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeRegisteredModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = featurestore_v1_feature_value_sync_service_pb2.ReconcileFeatureValuesResponse()
            outgoing_0 = featurestore_v1_feature_value_sync_service_pb2.ReconcileFeatureValuesRequest(
                context=request.context,
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    measurements=[
                        featurestore_v1_featurestore_pb2.FeatureValueMeasurement(
                            unit=request.registered_model.dimensions.unit
                        )
                    ]
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                featurestore_v1_feature_value_sync_service_pb2.ReconcileFeatureValuesRequest()
            )
            response_0 = await deps.clients.featurestore_feature_value_sync.ReconcileFeatureValues(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.feature_value.subject.code
            if returned_0_1:
                response.registered_model.code = returned_0_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.capacity
            response.registered_model.capacity = echoed_1
            return response

    async def handle_retry_registered_model_workflow(
        self,
        request: modelregistry_v1_registered_model_workflow_service_pb2.RetryRegisteredModelWorkflowRequest
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.RetryRegisteredModelWorkflowResponse:
        """Retrys a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_workflow_service_pb2.RetryRegisteredModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryRegisteredModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryRegisteredModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsResponse()
            response_1 = metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesResponse()
            outgoing_0 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsRequest(
                context=request.context,
                details=customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.registered_model.address.lines),
                        region=request.registered_model.address.region
                    )
                )
            )
            outgoing_1 = metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.registered_model.address.country_code
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.customers_consent_record_calculation.CompareConsentRecordOptions(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.metrics_metric_series_admin.RepairMetricSeries(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.consent_record.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.metric_series.tags
            response.registered_model.tags.extend(returned_1_0)
            returned_1_1 = response_1.metric_series.dimensions.weight
            if returned_1_1:
                response.registered_model.dimensions.weight = returned_1_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.owner
            response.registered_model.owner.CopyFrom(echoed_1)
            return response

    async def handle_signal_registered_model_workflow(
        self,
        request: modelregistry_v1_registered_model_workflow_service_pb2.SignalRegisteredModelWorkflowRequest
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.SignalRegisteredModelWorkflowResponse:
        """Signals a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_workflow_service_pb2.SignalRegisteredModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalRegisteredModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalRegisteredModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = customers_v1_customer_service_pb2.CreateCustomerResponse()
            response_1 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse()
            response_2 = customers_v1_household_validation_service_pb2.ScoreHouseholdResponse()
            response_3 = modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionResponse()
            outgoing_0 = customers_v1_customer_service_pb2.CreateCustomerRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.registered_model.audit.created_by,
                        etag=request.registered_model.audit.etag
                    ),
                    relationship_manager=identity_v1_refs_pb2.UserRef(email=request.registered_model.owner.email)
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = customers_v1_customer_service_pb2.CreateCustomerRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.customers_customer.CreateCustomer(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(region=response_0.customer.primary_address.region),
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.customer.audit.updated_by),
                    dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(
                        length=request.registered_model.dimensions.length
                    ),
                    owner=identity_v1_refs_pb2.UserRef(user_id=response_0.customer.relationship_manager.user_id)
                )
            )
            registered_1 = cast(
                modelregistry_v1_registered_model_sync_service_pb2_grpc.RegisteredModelSyncServiceStub,
                deps.clients.registry['acme.modelregistry.v1.RegisteredModelSyncService']
            )
            response_1 = await registered_1.ReconcileRegisteredModels(outgoing_1, timeout=deps.settings.timeout)
            outgoing_2 = customers_v1_household_validation_service_pb2.ScoreHouseholdRequest()
            outgoing_2.context.CopyFrom(request.context)
            if response_1.registered_model.WhichOneof('locator') == 'address':
                field_2_1_part_1 = outgoing_2.household.children.add()
                field_2_1_part_2 = field_2_1_part_1.children.add()
                field_2_1_part_2.location.lines.extend(list(response_1.registered_model.address.lines))
            if response_1.registered_model.WhichOneof('locator') == 'address':
                field_2_2_part_1 = outgoing_2.household.children.add()
                field_2_2_part_2 = field_2_2_part_1.children.add()
                field_2_2_part_2.location.region = response_1.registered_model.address.region
            field_2_3_part_1 = outgoing_2.household.children.add()
            field_2_3_part_2 = field_2_3_part_1.children.add()
            field_2_3_part_2.audit.created_by = response_0.customer.audit.created_by
            if request.registered_model.WhichOneof('locator') == 'address':
                field_2_4_part_1 = outgoing_2.household.children.add()
                field_2_4_part_2 = field_2_4_part_1.children.add()
                field_2_4_part_2.location.country_code = request.registered_model.address.country_code
            response_2 = await deps.clients.customers_household_validation.ScoreHousehold(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            command_3 = RegisteredModelWorkflowSignalRegisteredModelWorkflow3Command.model_validate(
                {
                    'context': request.context,
                    'model_version_subject_display_name': response_0.customer.relationship_manager.display_name
                }
            )
            outgoing_3 = to_registered_model_workflow_signal_registered_model_workflow3_command(command_3)
            response_3 = await deps.clients.modelregistry_model_version_approval.RecallModelVersion(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.registered_model.audit.updated_by
            if returned_1_0:
                response.registered_model.audit.updated_by = returned_1_0
            returned_1_1 = response_1.registered_model.dimensions.length
            if returned_1_1:
                response.registered_model.dimensions.length = returned_1_1
            returned_2_0 = response_2.household.audit.updated_by
            if returned_2_0:
                response.registered_model.audit.updated_by = returned_2_0
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.result.message = returned_3_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.code
            response.registered_model.code = echoed_1
            return response

    async def handle_start_registered_model_workflow(
        self,
        request: modelregistry_v1_registered_model_workflow_service_pb2.StartRegisteredModelWorkflowRequest
    ) -> modelregistry_v1_registered_model_workflow_service_pb2.StartRegisteredModelWorkflowResponse:
        """Starts a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_workflow_service_pb2.StartRegisteredModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartRegisteredModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartRegisteredModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = customers_v1_household_calculation_service_pb2.ExplainHouseholdCalculationResponse()
            response_1 = modelregistry_v1_model_version_approval_service_pb2.EscalateModelVersionResponse()
            outgoing_0 = customers_v1_household_calculation_service_pb2.ExplainHouseholdCalculationRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            audit=common_v1_audit_pb2.AuditInfo(updated_at=request.registered_model.audit.updated_at),
                            children=[
                                customers_v1_customers_pb2.Household(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_by=request.registered_model.audit.created_by
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.registered_model.owner.email)
                                )
                            ]
                        )
                    ]
                )
            )
            send_0 = partial(
                deps.clients.customers_household_calculation.ExplainHouseholdCalculation,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            outgoing_1 = modelregistry_v1_model_version_approval_service_pb2.EscalateModelVersionRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    measurements=[
                        modelregistry_v1_modelregistry_pb2.ModelVersionMeasurement(
                            unit=request.registered_model.dimensions.unit
                        )
                    ]
                )
            )
            response_1 = await hooks.registered_model_workflow_start_registered_model_workflow1(
                deps.clients.modelregistry_model_version_approval,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.household.audit.updated_by
            if returned_0_0:
                response.registered_model.audit.updated_by = returned_0_0
            returned_0_1 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_1)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.capacity
            response.registered_model.capacity = echoed_1
            return response
