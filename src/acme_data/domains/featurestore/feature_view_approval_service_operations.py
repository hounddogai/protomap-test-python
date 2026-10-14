"""Functional operations behind FeatureViewApprovalService."""

from __future__ import annotations

from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.banking.v1 import bank_account_query_service_pb2 as banking_v1_bank_account_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import dataset_version_query_service_pb2 as datasets_v1_dataset_version_query_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2_grpc as featurestore_v1_entity_reporting_service_pb2_grpc
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import (
    feature_value_lifecycle_service_pb2 as featurestore_v1_feature_value_lifecycle_service_pb2,
)
from acme.featurestore.v1 import feature_view_approval_service_pb2 as featurestore_v1_feature_view_approval_service_pb2
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import FeatureViewApprovalCommentFeatureViewApproval1Adapter
from acme_data.domains.featurestore.adapters import FeatureViewApprovalCommentFeatureViewApproval1Port
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureViewApprovalRejectFeatureView3Command
from acme_data.domains.featurestore.models import to_feature_view_approval_reject_feature_view3_command
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_approve_feature_view(
    deps: Dependencies,
    request: featurestore_v1_feature_view_approval_service_pb2.ApproveFeatureViewRequest
) -> featurestore_v1_feature_view_approval_service_pb2.ApproveFeatureViewResponse:
    """Approves a feature view."""
    response = featurestore_v1_feature_view_approval_service_pb2.ApproveFeatureViewResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ApproveFeatureView', extra={'fields': {'approver_email': request.details.approver_email}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ApproveFeatureView',
            {'approver_email': request.details.approver_email}
        )
        await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
        response_0 = featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsResponse()
        response_1 = datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsResponse()
        outgoing_0 = featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsRequest(
            context=request.context,
            filter=featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsRequest.Filter(
                created_after=request.feature_view.audit.created_at,
                labels=dict(request.feature_view.specs),
                owner_id=request.feature_view_id,
                region=request.feature_view.address.region
            )
        )
        response_0 = await deps.clients.featurestore_entity_reporting.CountEntityTotals(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsRequest(
            annotations=dict(request.annotations),
            context=request.context,
            details=datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsRequest.Details(
                filters=dict(request.feature_view.specs)
            ),
            reason=request.reason
        )
        response_1 = await hooks.feature_view_approval_approve_feature_view1(
            deps.clients.datasets_dataset_version_query,
            outgoing_1,
            deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.result.message = returned_0_1
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        echoed_0 = request.feature_view_id
        response.feature_view.feature_view_id = echoed_0
        echoed_1 = request.feature_view.capacity
        response.feature_view.capacity = echoed_1
        return response


async def handle_comment_feature_view_approval(
    deps: Dependencies,
    request: featurestore_v1_feature_view_approval_service_pb2.CommentFeatureViewApprovalRequest
) -> featurestore_v1_feature_view_approval_service_pb2.CommentFeatureViewApprovalResponse:
    """Comments a feature view."""
    response = featurestore_v1_feature_view_approval_service_pb2.CommentFeatureViewApprovalResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CommentFeatureViewApproval', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CommentFeatureViewApproval', {'reason': request.reason})
        await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
        response_0 = featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsResponse()
        response_1 = identity_v1_user_validation_service_pb2.NormalizeUserResponse()
        response_2 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewResponse()
        outgoing_0 = featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsRequest(
            context=request.context,
            feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                address=common_v1_address_pb2.PostalAddress(locality=request.feature_view.address.locality),
                audit=common_v1_audit_pb2.AuditInfo(created_by=request.feature_view.audit.created_by)
            )
        )
        response_0 = await deps.clients.featurestore_feature_view_sync.SyncFeatureViews(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = identity_v1_user_validation_service_pb2.NormalizeUserRequest(
            context=request.context,
            user=identity_v1_identity_pb2.User(
                primary_address=common_v1_address_pb2.PostalAddress(
                    country_code=response_0.feature_view.address.country_code,
                    postal_code=response_0.feature_view.address.postal_code
                )
            )
        )
        port_1: FeatureViewApprovalCommentFeatureViewApproval1Port = FeatureViewApprovalCommentFeatureViewApproval1Adapter(
            deps.clients.identity_user_validation,
            deps.settings.timeout
        )
        response_1 = await port_1.execute(outgoing_1)
        outgoing_2 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewRequest(
            context=request.context,
            feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                dimensions=featurestore_v1_featurestore_pb2.FeatureViewDimensions(
                    weight=response_0.feature_view.dimensions.weight
                )
            )
        )
        steps_2 = [
            partial(
                deps.clients.featurestore_feature_view_sync.PushFeatureView,
                outgoing_2,
                timeout=deps.settings.timeout
            )
        ]
        results_2 = await run_steps(steps_2)
        response_2 = results_2[-1]
        returned_0_0 = response_0.feature_view.specs
        response.feature_view.specs.update(returned_0_0)
        returned_1_0 = response_1.user.user_id
        if returned_1_0:
            response.feature_view.owner.user_id = returned_1_0
        returned_2_0 = response_2.feature_view.audit.created_at
        if returned_2_0.ListFields():
            response.feature_view.audit.created_at.MergeFrom(returned_2_0)
        returned_2_1 = response_2.feature_view.tags
        response.feature_view.tags.extend(returned_2_1)
        echoed_0 = request.feature_view_id
        response.feature_view.feature_view_id = echoed_0
        echoed_1 = request.feature_view.name
        response.feature_view.name = echoed_1
        return response


async def handle_delegate_feature_view_approval(
    deps: Dependencies,
    request: featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalRequest
) -> featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalResponse:
    """Delegates a feature view."""
    response = featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('DelegateFeatureViewApproval', extra={'fields': {'feature_view_id': request.feature_view_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'DelegateFeatureViewApproval',
            {'feature_view_id': request.feature_view_id}
        )
        await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
        response_0 = datasets_v1_dataset_query_service_pb2.CountDatasetsResponse()
        response_1 = featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateResponse()
        outgoing_0 = datasets_v1_dataset_query_service_pb2.CountDatasetsRequest(
            context=request.context,
            filter=datasets_v1_dataset_query_service_pb2.CountDatasetsRequest.Filter(
                created_after=request.feature_view.audit.created_at,
                owner_id=request.feature_view.owner.user_id,
                region=request.feature_view.address.region
            )
        )
        response_0 = await deps.clients.datasets_dataset_query.CountDatasets(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateRequest(
            context=request.context,
            feature_view_id=request.feature_view.feature_view_id
        )
        response_1 = cast(featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateResponse, await deps.bus.request(
            'acme.featurestore.v1.FeatureViewApprovalService/DelegateFeatureViewApproval/1', outgoing_1, deps.settings.timeout,
        ))
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.feature_view.feature_view_id
        if returned_1_0:
            response.feature_view.feature_view_id = returned_1_0
        echoed_0 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_0)
        echoed_1 = request.feature_view.code
        response.feature_view.code = echoed_1
        return response


async def handle_escalate_feature_view(
    deps: Dependencies,
    request: featurestore_v1_feature_view_approval_service_pb2.EscalateFeatureViewRequest
) -> featurestore_v1_feature_view_approval_service_pb2.EscalateFeatureViewResponse:
    """Escalates a feature view."""
    response = featurestore_v1_feature_view_approval_service_pb2.EscalateFeatureViewResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('EscalateFeatureView', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'EscalateFeatureView', {'reason': request.reason})
        await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
        response_0 = datasets_v1_dataset_version_query_service_pb2.ResolveDatasetVersionsResponse()
        response_1 = featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryResponse()
        response_2 = featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsResponse()
        outgoing_0 = datasets_v1_dataset_version_query_service_pb2.ResolveDatasetVersionsRequest(
            context=request.context
        )
        response_0 = await deps.clients.datasets_dataset_version_query.ResolveDatasetVersions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryRequest(
            context=request.context,
            details=featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(email=request.feature_view.owner.email)
            ),
            feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                measurements=[
                    featurestore_v1_featurestore_pb2.FeatureValueMeasurement(unit=request.feature_view.dimensions.unit)
                ],
                subject=datasets_v1_refs_pb2.DatasetRef(
                    code=request.feature_view.code,
                    display_name=request.feature_view.owner.display_name
                )
            )
        )
        method_name_1 = 'ScheduleFeatureValueExpiry'
        response_1 = await getattr(
            deps.clients.featurestore_feature_value_lifecycle,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        fields_2: dict[str, Any] = {
            'context': request.context,
            'filter': {
                'created_after': request.feature_view.audit.created_at,
                'labels': dict(request.feature_view.specs),
                'owner_id': response_1.feature_value.subject.dataset_id,
                'region': request.feature_view.address.region
            }
        }
        outgoing_2 = featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsRequest(**fields_2)
        response_2 = await deps.clients.featurestore_feature_view_query.CountFeatureViews(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.result.details
        response.result.details.update(returned_1_1)
        returned_2_0 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_0)
        returned_2_1 = response_2.result.message
        if returned_2_1:
            response.result.message = returned_2_1
        echoed_0 = request.feature_view_id
        response.feature_view.feature_view_id = echoed_0
        echoed_1 = request.feature_view.owner
        response.feature_view.owner.CopyFrom(echoed_1)
        return response


async def handle_recall_feature_view(
    deps: Dependencies,
    request: featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewRequest
) -> featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewResponse:
    """Recalls a feature view."""
    response = featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RecallFeatureView', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RecallFeatureView', {'reason': request.reason})
        await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
        response_0 = anomalies_v1_anomaly_approval_service_pb2.RecallAnomalyResponse()
        response_1 = featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsResponse()
        outgoing_0 = anomalies_v1_anomaly_approval_service_pb2.RecallAnomalyRequest(
            anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                audit=common_v1_audit_pb2.AuditInfo(created_by=request.feature_view.audit.created_by)
            ),
            context=request.context
        )
        response_0 = await deps.clients.anomalies_anomaly_approval.RecallAnomaly(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest(
            context=request.context,
            filter=featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest.Filter(
                created_after=response_0.anomaly.audit.updated_at,
                region=request.feature_view.address.region
            )
        )
        document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = Parse(
            document_1,
            featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest()
        )
        response_1 = await deps.clients.featurestore_feature_value_import.ListFeatureValueImports(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.anomaly.audit.etag
        if returned_0_0:
            response.feature_view.audit.etag = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.outcome.message = returned_1_0
        echoed_0 = request.feature_view_id
        response.feature_view.feature_view_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_reject_feature_view(
    deps: Dependencies,
    request: featurestore_v1_feature_view_approval_service_pb2.RejectFeatureViewRequest
) -> featurestore_v1_feature_view_approval_service_pb2.RejectFeatureViewResponse:
    """Rejects a feature view."""
    response = featurestore_v1_feature_view_approval_service_pb2.RejectFeatureViewResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RejectFeatureView', extra={'fields': {'approver_email': request.details.approver_email}})
        await deps.repository.audit(
            request.context.tenant_id,
            'RejectFeatureView',
            {'approver_email': request.details.approver_email}
        )
        await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
        response_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackResponse()
        response_1 = datasets_v1_dataset_validation_service_pb2.ScoreDatasetResponse()
        response_2 = featurestore_v1_entity_reporting_service_pb2.ScheduleEntityReportResponse()
        response_3 = anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackResponse()
        outgoing_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest(
            anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.details.approver.display_name)
            ),
            context=request.context,
            details=anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(display_name=request.feature_view.owner.display_name)
            )
        )
        response_0 = await deps.clients.anomalies_anomaly_feedback_approval.EscalateAnomalyFeedback(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = datasets_v1_dataset_validation_service_pb2.ScoreDatasetRequest()
        outgoing_1.context.CopyFrom(request.context)
        if request.feature_view.WhichOneof('locator') == 'address':
            outgoing_1.dataset.address.country_code = request.feature_view.address.country_code
        response_1 = await deps.clients.datasets_dataset_validation.ScoreDataset(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = featurestore_v1_entity_reporting_service_pb2.ScheduleEntityReportRequest(
            annotations=dict(request.annotations),
            context=request.context,
            details=featurestore_v1_entity_reporting_service_pb2.ScheduleEntityReportRequest.Details(
                filters=dict(response_0.anomaly_feedback.attributes)
            ),
            reason=request.reason
        )
        registered_2 = cast(
            featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceStub,
            deps.clients.registry['acme.featurestore.v1.EntityReportingService']
        )
        response_2 = await registered_2.ScheduleEntityReport(outgoing_2, timeout=deps.settings.timeout)
        command_3 = FeatureViewApprovalRejectFeatureView3Command(
            context=request.context,
            details_approver_user_id=request.details.approver.user_id,
            anomaly_feedback_subject_display_name=request.feature_view.owner.display_name,
            details_approver_display_name=request.details.approver.display_name,
            anomaly_feedback_kind=response_0.anomaly_feedback.kind
        )
        outgoing_3 = to_feature_view_approval_reject_feature_view3_command(command_3)
        response_3 = await deps.clients.anomalies_anomaly_feedback_approval.SubmitAnomalyFeedback(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_1_0 = response_1.dataset.audit.etag
        if returned_1_0:
            response.feature_view.audit.etag = returned_1_0
        returned_1_1 = response_1.dataset.components.get(
            'primary',
            datasets_v1_datasets_pb2.DatasetComponent()
        ).description
        if returned_1_1:
            response.feature_view.components['primary'].description = returned_1_1
        returned_2_0 = response_2.result.correlation_id
        if returned_2_0:
            response.result.correlation_id = returned_2_0
        returned_2_1 = response_2.result.status
        if returned_2_1:
            response.result.status = returned_2_1
        returned_3_0 = response_3.outcome.message
        if returned_3_0:
            response.outcome.message = returned_3_0
        echoed_0 = request.feature_view_id
        response.feature_view.feature_view_id = echoed_0
        echoed_1 = request.feature_view.code
        response.feature_view.code = echoed_1
        return response


async def handle_submit_feature_view(
    deps: Dependencies,
    request: featurestore_v1_feature_view_approval_service_pb2.SubmitFeatureViewRequest
) -> featurestore_v1_feature_view_approval_service_pb2.SubmitFeatureViewResponse:
    """Submits a feature view."""
    response = featurestore_v1_feature_view_approval_service_pb2.SubmitFeatureViewResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SubmitFeatureView', extra={'fields': {'approver_email': request.details.approver_email}})
        await deps.repository.audit(
            request.context.tenant_id,
            'SubmitFeatureView',
            {'approver_email': request.details.approver_email}
        )
        await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
        response_0 = datasets_v1_dataset_version_query_service_pb2.CountDatasetVersionsResponse()
        response_1 = banking_v1_bank_account_query_service_pb2.SummarizeBankAccountsResponse()
        response_2 = datasets_v1_dataset_validation_service_pb2.LintDatasetsResponse()
        response_3 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewResponse()
        outgoing_0 = datasets_v1_dataset_version_query_service_pb2.CountDatasetVersionsRequest(
            context=request.context,
            filter=datasets_v1_dataset_version_query_service_pb2.CountDatasetVersionsRequest.Filter(
                created_after=request.feature_view.audit.updated_at,
                owner_id=request.feature_view.components.get(
                    'primary',
                    featurestore_v1_featurestore_pb2.FeatureViewComponent()
                ).component_id,
                region=request.feature_view.address.region
            )
        )
        outgoing_1 = banking_v1_bank_account_query_service_pb2.SummarizeBankAccountsRequest(
            annotations=dict(request.annotations),
            context=request.context,
            reason=request.reason
        )
        outgoing_2 = datasets_v1_dataset_validation_service_pb2.LintDatasetsRequest(
            context=request.context,
            dataset=datasets_v1_datasets_pb2.Dataset(
                address=common_v1_address_pb2.PostalAddress(locality=request.feature_view.address.locality),
                audit=common_v1_audit_pb2.AuditInfo(updated_by=request.feature_view.audit.updated_by),
                dimensions=datasets_v1_datasets_pb2.DatasetDimensions(width=request.feature_view.dimensions.width)
            )
        )
        outgoing_3 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewRequest(
            context=request.context,
            feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                components={
                    'primary': featurestore_v1_featurestore_pb2.FeatureViewComponent(
                        quantity=request.feature_view.components.get(
                            'primary',
                            featurestore_v1_featurestore_pb2.FeatureViewComponent()
                        ).quantity
                    )
                }
            )
        )
        response_0, response_1, response_2, response_3 = await asyncio.gather(
            deps.clients.datasets_dataset_version_query.CountDatasetVersions(outgoing_0, timeout=deps.settings.timeout),
            deps.clients.banking_bank_account_query.SummarizeBankAccounts(outgoing_1, timeout=deps.settings.timeout),
            deps.clients.datasets_dataset_validation.LintDatasets(outgoing_2, timeout=deps.settings.timeout),
            deps.clients.featurestore_feature_view_sync.PushFeatureView(outgoing_3, timeout=deps.settings.timeout),
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.outcome.message = returned_1_0
        returned_2_0 = response_2.outcome.reference_id
        if returned_2_0:
            response.outcome.reference_id = returned_2_0
        returned_3_0 = response_3.result.status
        if returned_3_0:
            response.outcome.status = returned_3_0
        echoed_0 = request.feature_view_id
        response.feature_view.feature_view_id = echoed_0
        echoed_1 = request.feature_view.specs
        response.feature_view.specs.update(echoed_1)
        return response
