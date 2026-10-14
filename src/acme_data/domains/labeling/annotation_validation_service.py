"""Checks annotations against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
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
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.drivers.v1 import refs_pb2 as drivers_v1_refs_pb2
from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import (
    annotation_validation_service_pb2_grpc as labeling_v1_annotation_validation_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.maintenance.v1 import maintenance_pb2 as maintenance_v1_maintenance_pb2
from acme.maintenance.v1 import work_order_calculation_service_pb2 as maintenance_v1_work_order_calculation_service_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2_grpc as modelregistry_v1_deployment_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2
from acme.secrets.v1 import secret_service_pb2 as secrets_v1_secret_service_pb2
from acme.yards.v1 import yard_calculation_service_pb2 as yards_v1_yard_calculation_service_pb2
from acme.yards.v1 import yards_pb2 as yards_v1_yards_pb2

from acme_data.domains.labeling import hooks
from acme_data.domains.labeling.adapters import AnnotationValidationNormalizeAnnotation0Adapter
from acme_data.domains.labeling.adapters import AnnotationValidationNormalizeAnnotation0Port
from acme_data.domains.labeling.adapters import AnnotationValidationPreviewAnnotation0Adapter
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import AnnotationValidationExplainAnnotationDecision1Command
from acme_data.domains.labeling.models import to_annotation_validation_explain_annotation_decision1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnnotationValidationServicer(
    labeling_v1_annotation_validation_service_pb2_grpc.AnnotationValidationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckAnnotationEligibility(
        self, request: labeling_v1_annotation_validation_service_pb2.CheckAnnotationEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_validation_service_pb2.CheckAnnotationEligibilityResponse:
        """Checks an annotation."""
        return await self.handle_check_annotation_eligibility(request)

    @rpc_errors
    async def ExplainAnnotationDecision(
        self, request: labeling_v1_annotation_validation_service_pb2.ExplainAnnotationDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_validation_service_pb2.ExplainAnnotationDecisionResponse:
        """Explains an annotation."""
        return await self.handle_explain_annotation_decision(request)

    @rpc_errors
    async def LintAnnotations(
        self, request: labeling_v1_annotation_validation_service_pb2.LintAnnotationsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_validation_service_pb2.LintAnnotationsResponse:
        """Lints an annotation."""
        return await self.handle_lint_annotations(request)

    @rpc_errors
    async def NormalizeAnnotation(
        self, request: labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationResponse:
        """Normalizes an annotation."""
        return await self.handle_normalize_annotation(request)

    @rpc_errors
    async def PreviewAnnotation(
        self, request: labeling_v1_annotation_validation_service_pb2.PreviewAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_validation_service_pb2.PreviewAnnotationResponse:
        """Previews an annotation."""
        return await self.handle_preview_annotation(request)

    @rpc_errors
    async def ScoreAnnotation(
        self, request: labeling_v1_annotation_validation_service_pb2.ScoreAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_validation_service_pb2.ScoreAnnotationResponse:
        """Scores an annotation."""
        return await self.handle_score_annotation(request)

    @rpc_errors
    async def ValidateAnnotation(
        self, request: labeling_v1_annotation_validation_service_pb2.ValidateAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_validation_service_pb2.ValidateAnnotationResponse:
        """Validates an annotation."""
        return await self.handle_validate_annotation(request)

    async def handle_check_annotation_eligibility(
        self,
        request: labeling_v1_annotation_validation_service_pb2.CheckAnnotationEligibilityRequest
    ) -> labeling_v1_annotation_validation_service_pb2.CheckAnnotationEligibilityResponse:
        """Checks an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_validation_service_pb2.CheckAnnotationEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckAnnotationEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckAnnotationEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_validation_service_pb2.LintLabelingTasksResponse()
            response_1 = metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsResponse()
            response_2 = secrets_v1_secret_service_pb2.ListSecretsResponse()
            outgoing_0 = labeling_v1_labeling_task_validation_service_pb2.LintLabelingTasksRequest(
                context=request.context,
                details=labeling_v1_labeling_task_validation_service_pb2.LintLabelingTasksRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
                ),
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.contact.email),
                    customer=labeling_v1_refs_pb2.LabelSetRef(display_name=request.annotation.subject.display_name),
                    labeling_task_id=request.annotation.subject.labeling_task_id
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, labeling_v1_labeling_task_validation_service_pb2.LintLabelingTasksRequest())
            response_0 = await deps.clients.labeling_labeling_task_validation.LintLabelingTasks(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.created_after.CopyFrom(response_0.labeling_task.sla.due_at)
            outgoing_1.filter.owner_id = request.annotation.subject.labeling_task_id
            outgoing_1.filter.labels.update(dict(request.annotation.attributes))
            merged_1 = metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.metrics_metric_alert_notification.ListMetricAlertSubscriptions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = secrets_v1_secret_service_pb2.ListSecretsRequest(
                context=request.context,
                filter=secrets_v1_secret_service_pb2.ListSecretsRequest.Filter(
                    created_after=request.annotation.occurred_at,
                    labels=dict(request.annotation.attributes),
                    owner_id=request.annotation.subject.labeling_task_id
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = secrets_v1_secret_service_pb2.ListSecretsRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.secrets_secret.ListSecrets(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.labeling_task.assignee.display_name
            if returned_0_0:
                response.annotation.subject.display_name = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.correlation_id
            response.annotation.correlation_id = echoed_1
            return response

    async def handle_explain_annotation_decision(
        self,
        request: labeling_v1_annotation_validation_service_pb2.ExplainAnnotationDecisionRequest
    ) -> labeling_v1_annotation_validation_service_pb2.ExplainAnnotationDecisionResponse:
        """Explains an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_validation_service_pb2.ExplainAnnotationDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainAnnotationDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainAnnotationDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsResponse()
            response_1 = labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskResponse()
            response_2 = labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationResponse()
            response_3 = labeling_v1_label_set_calculation_service_pb2.CompareLabelSetOptionsResponse()
            outgoing_0 = modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=request.details.contact.email,
                                name=request.details.contact.name,
                                phone=request.details.contact.phone
                            )
                        )
                    ]
                )
            )
            registered_0 = cast(
                modelregistry_v1_deployment_calculation_service_pb2_grpc.DeploymentCalculationServiceStub,
                deps.clients.registry['acme.modelregistry.v1.DeploymentCalculationService']
            )
            response_0 = await registered_0.RecalculateDeployments(outgoing_0, timeout=deps.settings.timeout)
            command_1 = AnnotationValidationExplainAnnotationDecision1Command(
                context=request.context,
                labeling_task_requester_preferred_channel=request.details.contact.preferred_channel,
                labeling_task_requester_email=request.details.contact.email
            )
            outgoing_1 = to_annotation_validation_explain_annotation_decision1_command(command_1)
            response_1 = await deps.clients.labeling_labeling_task_calculation.EstimateLabelingTask(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            requests_2: list[labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationRequest] = []
            for item_2 in request.annotation.measurements:
                outgoing_2 = labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationRequest(
                    annotation=labeling_v1_labeling_pb2.Annotation(
                        measurements=[
                            labeling_v1_labeling_pb2.AnnotationMeasurement(
                                metric=item_2.metric,
                                observed_at=item_2.observed_at,
                                value=item_2.value
                            )
                        ]
                    ),
                    context=request.context
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.labeling_annotation_calculation.SimulateAnnotation(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            outgoing_3 = labeling_v1_label_set_calculation_service_pb2.CompareLabelSetOptionsRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_by=response_0.deployment.audit.created_by
                                    ),
                                    location=common_v1_address_pb2.PostalAddress(
                                        locality=response_0.deployment.location.locality
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            send_3 = partial(
                deps.clients.labeling_label_set_calculation.CompareLabelSetOptions,
                timeout=deps.settings.timeout
            )
            response_3 = await send_3(outgoing_3)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_3_0 = response_3.label_set.manager.display_name
            if returned_3_0:
                response.annotation.subject.display_name = returned_3_0
            returned_3_1 = response_3.label_set.attributes
            response.annotation.attributes.update(returned_3_1)
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.occurred_at
            response.annotation.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_lint_annotations(
        self,
        request: labeling_v1_annotation_validation_service_pb2.LintAnnotationsRequest
    ) -> labeling_v1_annotation_validation_service_pb2.LintAnnotationsResponse:
        """Lints an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_validation_service_pb2.LintAnnotationsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintAnnotations', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintAnnotations', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationResponse()
            response_1 = secrets_v1_secret_service_pb2.SearchSecretsResponse()
            outgoing_0 = labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.annotation.subject.display_name),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
                ),
                labeling_task_id=request.annotation.subject.labeling_task_id
            )
            response_0 = await hooks.annotation_validation_lint_annotations0(
                deps.clients.labeling_labeling_task_calculation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = secrets_v1_secret_service_pb2.SearchSecretsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.created_after.CopyFrom(response_0.labeling_task.audit.created_at)
            outgoing_1.filter.owner_id = response_0.outcome.reference_id
            outgoing_1.filter.labels.update(dict(request.annotation.attributes))
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.secrets_secret.SearchSecrets(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.subject
            response.annotation.subject.CopyFrom(echoed_1)
            return response

    async def handle_normalize_annotation(
        self,
        request: labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationRequest
    ) -> labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationResponse:
        """Normalizes an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeAnnotation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeAnnotation', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = ledger_v1_ledger_account_service_pb2.ListLedgerAccountsResponse()
            response_1 = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationResponse()
            outgoing_0 = ledger_v1_ledger_account_service_pb2.ListLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_service_pb2.ListLedgerAccountsRequest.Filter(
                    created_after=request.annotation.occurred_at
                )
            )
            port_0: AnnotationValidationNormalizeAnnotation0Port = AnnotationValidationNormalizeAnnotation0Adapter(
                deps.clients.ledger_ledger_account,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(annotation_id=request.annotation.annotation_id),
                context=request.context
            )
            steps_1 = [
                partial(
                    deps.clients.labeling_annotation_calculation.CalculateAnnotation,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.annotation.attributes
            response.annotation.attributes.update(returned_1_0)
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_preview_annotation(
        self,
        request: labeling_v1_annotation_validation_service_pb2.PreviewAnnotationRequest
    ) -> labeling_v1_annotation_validation_service_pb2.PreviewAnnotationResponse:
        """Previews an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_validation_service_pb2.PreviewAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewAnnotation', extra={'fields': {'correlation_id': request.annotation.correlation_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PreviewAnnotation',
                {'correlation_id': request.annotation.correlation_id}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = featurestore_v1_feature_value_query_service_pb2.CountFeatureValuesResponse()
            response_1 = yards_v1_yard_calculation_service_pb2.EstimateYardResponse()
            outgoing_0 = featurestore_v1_feature_value_query_service_pb2.CountFeatureValuesRequest(
                context=request.context,
                filter=featurestore_v1_feature_value_query_service_pb2.CountFeatureValuesRequest.Filter(
                    created_after=request.annotation.occurred_at,
                    owner_id=request.annotation.annotation_id
                )
            )
            response_0 = await AnnotationValidationPreviewAnnotation0Adapter(
                deps.clients.featurestore_feature_value_query,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = yards_v1_yard_calculation_service_pb2.EstimateYardRequest(
                context=request.context,
                reason=request.reason,
                yard=yards_v1_yards_pb2.Yard(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.annotation.subject.display_name,
                        email=request.details.contact.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_1 = cast(yards_v1_yard_calculation_service_pb2.EstimateYardResponse, await deps.bus.request(
                'acme.labeling.v1.AnnotationValidationService/PreviewAnnotation/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.yard.dimensions.unit
            returned_1_0_part_1 = response.annotation.measurements.add()
            if returned_1_0:
                returned_1_0_part_1.unit = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.attributes
            response.annotation.attributes.update(echoed_1)
            return response

    async def handle_score_annotation(
        self,
        request: labeling_v1_annotation_validation_service_pb2.ScoreAnnotationRequest
    ) -> labeling_v1_annotation_validation_service_pb2.ScoreAnnotationResponse:
        """Scores an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_validation_service_pb2.ScoreAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreAnnotation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreAnnotation', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse()
            response_2 = search_v1_search_index_query_service_pb2.FindSearchIndexesResponse()
            outgoing_0 = labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    customer=labeling_v1_refs_pb2.LabelSetRef(display_name=request.annotation.subject.display_name),
                    labeling_task_id=request.annotation.subject.labeling_task_id,
                    priority=request.annotation.subject.priority
                )
            )
            response_0 = await deps.clients.labeling_labeling_task_calculation.ExplainLabelingTaskCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        lines=list(request.details.destination.lines),
                        locality=request.details.destination.locality
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.labeling_task.customer.display_name)
                )
            )
            method_name_1 = 'EstimateRegisteredModel'
            response_1 = await getattr(
                deps.clients.modelregistry_registered_model_calculation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': response_1.registered_model.audit.created_at,
                    'region': request.details.destination.region
                }
            }
            outgoing_2 = search_v1_search_index_query_service_pb2.FindSearchIndexesRequest(**fields_2)
            response_2 = await deps.clients.search_search_index_query.FindSearchIndexes(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.subject
            response.annotation.subject.CopyFrom(echoed_1)
            return response

    async def handle_validate_annotation(
        self,
        request: labeling_v1_annotation_validation_service_pb2.ValidateAnnotationRequest
    ) -> labeling_v1_annotation_validation_service_pb2.ValidateAnnotationResponse:
        """Validates an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_validation_service_pb2.ValidateAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateAnnotation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateAnnotation', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskResponse()
            response_1 = maintenance_v1_work_order_calculation_service_pb2.SimulateWorkOrderResponse()
            response_2 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskResponse()
            outgoing_0 = labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    requester=common_v1_contact_pb2.ContactInfo(
                        name=request.details.contact.name,
                        phone=request.details.contact.phone
                    )
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskRequest()
            )
            response_0 = await deps.clients.labeling_labeling_task_validation.PreviewLabelingTask(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = maintenance_v1_work_order_calculation_service_pb2.SimulateWorkOrderRequest(
                context=request.context,
                work_order=maintenance_v1_maintenance_pb2.WorkOrder(
                    assignee=identity_v1_refs_pb2.UserRef(
                        email=request.details.contact.email,
                        user_id=response_0.labeling_task.assignee.user_id
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.labeling_task.audit.etag),
                    customer=drivers_v1_refs_pb2.DriverRef(display_name=response_0.labeling_task.customer.display_name)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, maintenance_v1_work_order_calculation_service_pb2.SimulateWorkOrderRequest())
            response_1 = await deps.clients.maintenance_work_order_calculation.SimulateWorkOrder(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.labeling_task.assignee.email = response_0.labeling_task.assignee.email
            outgoing_2.labeling_task.assignee.display_name = response_1.work_order.customer.display_name
            merged_2 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.labeling_labeling_task_calculation.QuoteLabelingTask(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.work_order.assignee.display_name
            if returned_1_0:
                response.annotation.subject.display_name = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.annotation.correlation_id = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.kind
            response.annotation.kind = echoed_1
            return response
