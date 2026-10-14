"""Moves a model version between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_query_service_pb2 as customers_v1_household_query_service_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_value_approval_service_pb2 as featurestore_v1_feature_value_approval_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_lifecycle_service_pb2 as modelregistry_v1_model_version_lifecycle_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_lifecycle_service_pb2_grpc as modelregistry_v1_model_version_lifecycle_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2 as modelregistry_v1_model_version_validation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2
from acme.modelregistry.v1 import (
    registered_model_service_pb2_grpc as modelregistry_v1_registered_model_service_pb2_grpc,
)
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import ModelVersionLifecycleActivateModelVersion3Command
from acme_data.domains.modelregistry.models import to_model_version_lifecycle_activate_model_version3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ModelVersionLifecycleServicer(
    modelregistry_v1_model_version_lifecycle_service_pb2_grpc.ModelVersionLifecycleServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ActivateModelVersion(
        self, request: modelregistry_v1_model_version_lifecycle_service_pb2.ActivateModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.ActivateModelVersionResponse:
        """Activates a model version."""
        return await self.handle_activate_model_version(request)

    @rpc_errors
    async def ExpireModelVersion(
        self, request: modelregistry_v1_model_version_lifecycle_service_pb2.ExpireModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.ExpireModelVersionResponse:
        """Expires a model version."""
        return await self.handle_expire_model_version(request)

    @rpc_errors
    @retry_transient
    async def GetModelVersionLifecycle(
        self, request: modelregistry_v1_model_version_lifecycle_service_pb2.GetModelVersionLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.GetModelVersionLifecycleResponse:
        """Returns a model version."""
        return await self.handle_get_model_version_lifecycle(request)

    @rpc_errors
    async def ReinstateModelVersion(
        self, request: modelregistry_v1_model_version_lifecycle_service_pb2.ReinstateModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.ReinstateModelVersionResponse:
        """Reinstates a model version."""
        return await self.handle_reinstate_model_version(request)

    @rpc_errors
    async def RenewModelVersion(
        self, request: modelregistry_v1_model_version_lifecycle_service_pb2.RenewModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.RenewModelVersionResponse:
        """Renews a model version."""
        return await self.handle_renew_model_version(request)

    @rpc_errors
    async def ScheduleModelVersionExpiry(
        self, request: modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryResponse:
        """Schedules a model version."""
        return await self.handle_schedule_model_version_expiry(request)

    @rpc_errors
    async def SuspendModelVersion(
        self, request: modelregistry_v1_model_version_lifecycle_service_pb2.SuspendModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.SuspendModelVersionResponse:
        """Suspends a model version."""
        return await self.handle_suspend_model_version(request)

    @rpc_errors
    async def TerminateModelVersion(
        self, request: modelregistry_v1_model_version_lifecycle_service_pb2.TerminateModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.TerminateModelVersionResponse:
        """Terminates a model version."""
        return await self.handle_terminate_model_version(request)

    async def handle_activate_model_version(
        self,
        request: modelregistry_v1_model_version_lifecycle_service_pb2.ActivateModelVersionRequest
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.ActivateModelVersionResponse:
        """Activates a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_lifecycle_service_pb2.ActivateModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivateModelVersion', {'reason': request.reason})
            response_0 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsResponse()
            response_1 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityResponse()
            response_2 = modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelResponse()
            response_3 = modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportResponse()
            outgoing_0 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.created_after.CopyFrom(request.details.effective_at)
            outgoing_0.filter.labels.update(dict(request.annotations))
            merged_0 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.metrics_metric_alert_query.BrowseMetricAlerts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.details.new_owner.email)
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.modelregistry_model_version_validation.CheckModelVersionEligibility(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=response_1.model_version.subject.display_name,
                        email=response_1.model_version.subject.email,
                        user_id=request.details.new_owner.user_id
                    )
                )
            )
            registered_2 = cast(
                modelregistry_v1_registered_model_service_pb2_grpc.RegisteredModelServiceStub,
                deps.clients.registry['acme.modelregistry.v1.RegisteredModelService']
            )
            response_2 = await registered_2.CloneRegisteredModel(outgoing_2, timeout=deps.settings.timeout)
            command_3 = ModelVersionLifecycleActivateModelVersion3Command(
                context=request.context,
                deployment_participants_contact_phone=request.details.notify_contact.phone
            )
            outgoing_3 = to_model_version_lifecycle_activate_model_version3_command(command_3)
            response_3 = await deps.clients.modelregistry_deployment_import.ValidateDeploymentImport(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.registered_model.owner.email
            if returned_2_0:
                response.model_version.subject.email = returned_2_0
            returned_3_0 = response_3.outcome.message
            if returned_3_0:
                response.result.message = returned_3_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_model_version(
        self,
        request: modelregistry_v1_model_version_lifecycle_service_pb2.ExpireModelVersionRequest
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.ExpireModelVersionResponse:
        """Expires a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_lifecycle_service_pb2.ExpireModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireModelVersion', {'reason': request.reason})
            response_0 = audit_v1_audit_event_service_pb2.ListAuditEventsResponse()
            response_1 = featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalResponse()
            response_2 = modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionResponse()
            response_3 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse()
            outgoing_0 = audit_v1_audit_event_service_pb2.ListAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_service_pb2.ListAuditEventsRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.annotations),
                    owner_id=request.details.new_owner.user_id
                )
            )
            outgoing_1 = featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalRequest(
                context=request.context,
                details=featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.details.new_owner.user_id)
                )
            )
            outgoing_2 = modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.details.notify_contact.name,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.details.notify_contact.email)
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.audit_audit_event.ListAuditEvents(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.featurestore_feature_value_approval.DelegateFeatureValueApproval(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.modelregistry_model_version_validation.NormalizeModelVersion(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_3 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.registered_model.owner.display_name = response_1.feature_value.subject.display_name
            outgoing_3.registered_model.owner.email = request.details.new_owner.email
            outgoing_3.registered_model.owner.user_id = request.details.new_owner.user_id
            outgoing_3.annotations.update(dict(request.annotations))
            outgoing_3.context.tenant_id = tenant_id.get()
            response_3 = await deps.clients.modelregistry_registered_model_calculation.EstimateRegisteredModel(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.feature_value.sequence
            if returned_1_0:
                response.model_version.sequence = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.model_version.sequence
            if returned_2_0:
                response.model_version.sequence = returned_2_0
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.result.message = returned_3_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_model_version_lifecycle(
        self,
        request: modelregistry_v1_model_version_lifecycle_service_pb2.GetModelVersionLifecycleRequest
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.GetModelVersionLifecycleResponse:
        """Returns a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_lifecycle_service_pb2.GetModelVersionLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetModelVersionLifecycle', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'GetModelVersionLifecycle', {})
            response_0 = customers_v1_household_query_service_pb2.BrowseHouseholdsResponse()
            outgoing_0 = customers_v1_household_query_service_pb2.BrowseHouseholdsRequest(
                context=request.context,
                filter=customers_v1_household_query_service_pb2.BrowseHouseholdsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.context.actor.user_id
                )
            )
            response_0 = await deps.clients.customers_household_query.BrowseHouseholds(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            return response

    async def handle_reinstate_model_version(
        self,
        request: modelregistry_v1_model_version_lifecycle_service_pb2.ReinstateModelVersionRequest
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.ReinstateModelVersionResponse:
        """Reinstates a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_lifecycle_service_pb2.ReinstateModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstateModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReinstateModelVersion', {'reason': request.reason})
            response_0 = notifications_v1_notification_query_service_pb2.CountNotificationsResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.CountNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_query_service_pb2.CountNotificationsRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.annotations),
                    owner_id=request.model_version_id
                )
            )
            steps_0 = [
                partial(
                    deps.clients.notifications_notification_query.CountNotifications,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.model_version.correlation_id = returned_0_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_renew_model_version(
        self,
        request: modelregistry_v1_model_version_lifecycle_service_pb2.RenewModelVersionRequest
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.RenewModelVersionResponse:
        """Renews a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_lifecycle_service_pb2.RenewModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewModelVersion', {'reason': request.reason})
            response_0 = customers_v1_consent_record_validation_service_pb2.NormalizeConsentRecordResponse()
            response_1 = customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationResponse()
            response_2 = customers_v1_customer_segment_validation_service_pb2.PreviewCustomerSegmentResponse()
            outgoing_0 = customers_v1_consent_record_validation_service_pb2.NormalizeConsentRecordRequest(
                context=request.context,
                details=customers_v1_consent_record_validation_service_pb2.NormalizeConsentRecordRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify_contact.email,
                        name=request.details.notify_contact.name,
                        phone=request.details.notify_contact.phone
                    )
                )
            )
            outgoing_2 = customers_v1_customer_segment_validation_service_pb2.PreviewCustomerSegmentRequest(
                context=request.context,
                details=customers_v1_customer_segment_validation_service_pb2.PreviewCustomerSegmentRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify_contact.email)
                )
            )
            response_0, response_2 = await asyncio.gather(
                deps.clients.customers_consent_record_validation.NormalizeConsentRecord(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.customers_customer_segment_validation.PreviewCustomerSegment(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_1 = customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.new_owner.email),
                    name=request.details.notify_contact.name,
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.new_owner.display_name,
                        email=request.details.notify_contact.email
                    )
                )
            )
            response_1 = cast(customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationResponse, await deps.bus.request(
                'acme.modelregistry.v1.ModelVersionLifecycleService/RenewModelVersion/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.model_version.correlation_id = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.outcome.reference_id
            if returned_1_1:
                response.outcome.reference_id = returned_1_1
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_schedule_model_version_expiry(
        self,
        request: modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryRequest
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryResponse:
        """Schedules a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleModelVersionExpiry', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleModelVersionExpiry',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsResponse()
            response_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackResponse()
            response_2 = modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionResponse()
            outgoing_0 = metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest.Filter(
                    created_after=request.model_version.occurred_at,
                    labels=dict(request.details.parameters)
                )
            )
            method_name_0 = 'CountMetricAlerts'
            response_0 = await getattr(
                deps.clients.metrics_metric_alert_query,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            requests_1: list[anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest] = []
            for item_1 in request.model_version.measurements:
                outgoing_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest(
                    anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                        measurements=[
                            anomalies_v1_anomalies_pb2.AnomalyFeedbackMeasurement(
                                metric=item_1.metric,
                                unit=item_1.unit,
                                value=item_1.value
                            )
                        ]
                    ),
                    context=request.context
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.anomalies_anomaly_feedback_approval.EscalateAnomalyFeedback(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            outgoing_2 = modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    organizer=identity_v1_refs_pb2.UserRef(
                        display_name=response_1.anomaly_feedback.subject.display_name
                    ),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                preferred_channel=request.details.notify.preferred_channel
                            )
                        )
                    ]
                ),
                details=modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(
                document_2,
                modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionRequest()
            )
            response_2 = await deps.clients.modelregistry_deployment_validation.ExplainDeploymentDecision(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.occurred_at
            response.model_version.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_suspend_model_version(
        self,
        request: modelregistry_v1_model_version_lifecycle_service_pb2.SuspendModelVersionRequest
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.SuspendModelVersionResponse:
        """Suspends a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_lifecycle_service_pb2.SuspendModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SuspendModelVersion', {'reason': request.reason})
            response_0 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceResponse()
            response_1 = featurestore_v1_feature_value_approval_service_pb2.ListPendingFeatureValuesResponse()
            outgoing_0 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.new_owner.display_name,
                        email=request.details.new_owner.email,
                        user_id=request.details.new_owner.user_id
                    )
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, customers_v1_preference_calculation_service_pb2.SimulatePreferenceRequest())
            response_0 = await deps.clients.customers_preference_calculation.SimulatePreference(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_approval_service_pb2.ListPendingFeatureValuesRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.created_after.CopyFrom(response_0.preference.audit.updated_at)
            merged_1 = featurestore_v1_feature_value_approval_service_pb2.ListPendingFeatureValuesRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.featurestore_feature_value_approval.ListPendingFeatureValues(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_model_version(
        self,
        request: modelregistry_v1_model_version_lifecycle_service_pb2.TerminateModelVersionRequest
    ) -> modelregistry_v1_model_version_lifecycle_service_pb2.TerminateModelVersionResponse:
        """Terminates a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_lifecycle_service_pb2.TerminateModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminateModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TerminateModelVersion', {'reason': request.reason})
            response_0 = customers_v1_consent_record_calculation_service_pb2.RecalculateConsentRecordsResponse()
            outgoing_0 = customers_v1_consent_record_calculation_service_pb2.RecalculateConsentRecordsRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    subject=customers_v1_refs_pb2.HouseholdRef(display_name=request.details.new_owner.display_name)
                ),
                context=request.context
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = customers_v1_consent_record_calculation_service_pb2.RecalculateConsentRecordsRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.customers_consent_record_calculation.RecalculateConsentRecords(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.consent_record.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
