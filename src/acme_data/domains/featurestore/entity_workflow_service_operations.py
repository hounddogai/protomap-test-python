"""Functional operations behind EntityWorkflowService."""

from __future__ import annotations

from typing import Any
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import detector_approval_service_pb2 as anomalies_v1_detector_approval_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.featurestore.v1 import entity_workflow_service_pb2 as featurestore_v1_entity_workflow_service_pb2
from acme.featurestore.v1 import (
    feature_value_approval_service_pb2 as featurestore_v1_feature_value_approval_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2 as featurestore_v1_feature_value_reporting_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2 as featurestore_v1_feature_view_reporting_service_pb2,
)
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.ledger.v1 import refs_pb2 as ledger_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2

from acme_data.domains.featurestore.adapters import EntityWorkflowResumeEntityWorkflow1Adapter
from acme_data.domains.featurestore.adapters import EntityWorkflowResumeEntityWorkflow1Port
from acme_data.domains.featurestore.adapters import EntityWorkflowResumeEntityWorkflow3Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import EntityWorkflowAdvanceEntityWorkflow2Command
from acme_data.domains.featurestore.models import to_entity_workflow_advance_entity_workflow2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_advance_entity_workflow(
    deps: Dependencies,
    request: featurestore_v1_entity_workflow_service_pb2.AdvanceEntityWorkflowRequest
) -> featurestore_v1_entity_workflow_service_pb2.AdvanceEntityWorkflowResponse:
    """Advances an entity."""
    response = featurestore_v1_entity_workflow_service_pb2.AdvanceEntityWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('AdvanceEntityWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'AdvanceEntityWorkflow', {'reason': request.reason})
        await deps.repository.save_entity(request.context.tenant_id, request.entity)
        response_0 = ledger_v1_ledger_account_validation_service_pb2.ExplainLedgerAccountDecisionResponse()
        response_1 = featureflags_v1_feature_flag_service_pb2.BatchCreateFeatureFlagsResponse()
        response_2 = featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsResponse()
        outgoing_0 = ledger_v1_ledger_account_validation_service_pb2.ExplainLedgerAccountDecisionRequest(
            context=request.context,
            details=ledger_v1_ledger_account_validation_service_pb2.ExplainLedgerAccountDecisionRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.entity.relationship_manager.email,
                    name=request.entity.contact.name
                )
            ),
            ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
                contact=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone),
                holder=ledger_v1_refs_pb2.PostingBatchRef(display_name=request.entity.relationship_manager.display_name)
            )
        )
        response_0 = await deps.clients.ledger_ledger_account_validation.ExplainLedgerAccountDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featureflags_v1_feature_flag_service_pb2.BatchCreateFeatureFlagsRequest(
            context=request.context,
            header=featureflags_v1_feature_flag_service_pb2.BatchCreateFeatureFlagsRequest.StreamHeader(
                submitted_by=common_v1_contact_pb2.ContactInfo(
                    preferred_channel=request.details.notify.preferred_channel
                )
            )
        )
        response_1 = await deps.clients.featureflags_feature_flag.BatchCreateFeatureFlags(
            async_messages((outgoing_1,)),
            timeout=deps.settings.timeout
        )
        command_2 = EntityWorkflowAdvanceEntityWorkflow2Command.model_validate(
            {
                'context': request.context,
                'filter_region': request.entity.primary_address.region,
                'filter_labels': dict(response_0.ledger_account.labels),
                'filter_created_after': response_0.ledger_account.audit.created_at,
                'filter_owner_id': request.entity.relationship_manager.user_id
            }
        )
        outgoing_2 = to_entity_workflow_advance_entity_workflow2_command(command_2)
        response_2 = await deps.clients.featurestore_feature_value_reporting.ListFeatureValueReports(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.ledger_account.audit.created_at
        if returned_0_0.ListFields():
            response.entity.audit.created_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.outcome.reference_id
        if returned_0_1:
            response.outcome.reference_id = returned_0_1
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.outcome.status = returned_2_0
        echoed_0 = request.entity_id
        response.entity.entity_id = echoed_0
        echoed_1 = request.entity.name
        response.entity.contact.name.CopyFrom(echoed_1)
        return response


async def handle_inspect_entity_workflow(
    deps: Dependencies,
    request: featurestore_v1_entity_workflow_service_pb2.InspectEntityWorkflowRequest
) -> featurestore_v1_entity_workflow_service_pb2.InspectEntityWorkflowResponse:
    """Returns an entity."""
    response = featurestore_v1_entity_workflow_service_pb2.InspectEntityWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('InspectEntityWorkflow', extra={'fields': {'domain': 'featurestore'}})
        await deps.repository.audit(request.context.tenant_id, 'InspectEntityWorkflow', {})
        response_0 = datasets_v1_dataset_validation_service_pb2.LintDatasetsResponse()
        outgoing_0 = datasets_v1_dataset_validation_service_pb2.LintDatasetsRequest(
            context=request.context,
            dataset=datasets_v1_datasets_pb2.Dataset(
                components={'primary': datasets_v1_datasets_pb2.DatasetComponent(component_id=request.entity_id)},
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            ),
            details=datasets_v1_dataset_validation_service_pb2.LintDatasetsRequest.Details(
                locale=request.context.locale
            )
        )
        response_0 = await deps.clients.datasets_dataset_validation.LintDatasets(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.dataset.owner.email
        if returned_0_0:
            response.entity.relationship_manager.email = returned_0_0
        returned_0_1 = response_0.dataset.address.region
        if returned_0_1:
            response.entity.primary_address.region = returned_0_1
        echoed_0 = request.entity_id
        response.entity.entity_id = echoed_0
        return response


async def handle_pause_entity_workflow(
    deps: Dependencies,
    request: featurestore_v1_entity_workflow_service_pb2.PauseEntityWorkflowRequest
) -> featurestore_v1_entity_workflow_service_pb2.PauseEntityWorkflowResponse:
    """Pauses an entity."""
    response = featurestore_v1_entity_workflow_service_pb2.PauseEntityWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PauseEntityWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PauseEntityWorkflow', {'reason': request.reason})
        await deps.repository.save_entity(request.context.tenant_id, request.entity)
        response_0 = datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaResponse()
        outgoing_0 = datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaRequest(
            context=request.context,
            data_schema=datasets_v1_datasets_pb2.DataSchema(
                children=[
                    datasets_v1_datasets_pb2.DataSchema(
                        children=[
                            datasets_v1_datasets_pb2.DataSchema(
                                audit=common_v1_audit_pb2.AuditInfo(created_at=request.entity.audit.created_at),
                                location=common_v1_address_pb2.PostalAddress(
                                    locality=request.entity.primary_address.locality
                                )
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.datasets_data_schema_validation.ScoreDataSchema(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.data_schema.location.country_code
        if returned_0_0:
            response.entity.primary_address.country_code = returned_0_0
        returned_0_1 = response_0.data_schema.audit.created_at
        if returned_0_1.ListFields():
            response.entity.audit.created_at.MergeFrom(returned_0_1)
        echoed_0 = request.entity_id
        response.entity.entity_id = echoed_0
        echoed_1 = request.entity.contact
        response.entity.contact.CopyFrom(echoed_1)
        return response


async def handle_resume_entity_workflow(
    deps: Dependencies,
    request: featurestore_v1_entity_workflow_service_pb2.ResumeEntityWorkflowRequest
) -> featurestore_v1_entity_workflow_service_pb2.ResumeEntityWorkflowResponse:
    """Resumes an entity."""
    response = featurestore_v1_entity_workflow_service_pb2.ResumeEntityWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ResumeEntityWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ResumeEntityWorkflow', {'reason': request.reason})
        await deps.repository.save_entity(request.context.tenant_id, request.entity)
        response_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse()
        response_1 = featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsResponse()
        response_2 = featurestore_v1_entity_approval_service_pb2.RecallEntityResponse()
        response_3 = featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalResponse()
        outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                subject=customers_v1_refs_pb2.CustomerRef(email=request.entity.relationship_manager.email)
            ),
            details=datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    lines=list(request.entity.primary_address.lines),
                    postal_code=request.entity.primary_address.postal_code,
                    recipient=request.entity.primary_address.recipient
                )
            )
        )
        response_0 = await deps.clients.datasets_dataset_version_calculation.CompareDatasetVersionOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsRequest(
            context=request.context,
            filter=featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsRequest.Filter(
                region=request.entity.primary_address.region
            )
        )
        port_1: EntityWorkflowResumeEntityWorkflow1Port = EntityWorkflowResumeEntityWorkflow1Adapter(
            deps.clients.featurestore_feature_view_sync,
            deps.settings.timeout
        )
        response_1 = await port_1.execute(outgoing_1)
        outgoing_2 = featurestore_v1_entity_approval_service_pb2.RecallEntityRequest()
        outgoing_2.context.CopyFrom(request.context)
        if request.entity.WhichOneof('identity_document') == 'passport':
            outgoing_2.entity.passport.number = request.entity.passport.number
        outgoing_2.entity.audit.etag = request.entity.audit.etag
        outgoing_2.entity.relationship_manager.email = request.details.notify.email
        response_2 = await deps.clients.featurestore_entity_approval.RecallEntity(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalRequest(
            context=request.context,
            details=featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(email=response_2.entity.relationship_manager.email)
            ),
            feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                subject=datasets_v1_refs_pb2.DatasetRef(display_name=response_0.dataset_version.subject.display_name)
            )
        )
        response_3 = await EntityWorkflowResumeEntityWorkflow3Adapter(
            deps.clients.featurestore_feature_value_approval,
            deps.settings.timeout
        )(outgoing_3)
        returned_0_0 = response_0.dataset_version.subject.email
        if returned_0_0:
            response.entity.relationship_manager.email = returned_0_0
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        returned_1_1 = response_1.result.correlation_id
        if returned_1_1:
            response.result.correlation_id = returned_1_1
        returned_2_0 = response_2.entity.primary_address.locality
        if returned_2_0:
            response.entity.primary_address.locality = returned_2_0
        returned_3_0 = response_3.outcome.status
        if returned_3_0:
            response.result.status = returned_3_0
        echoed_0 = request.entity_id
        response.entity.entity_id = echoed_0
        echoed_1 = request.entity.status
        response.entity.status = echoed_1
        return response


async def handle_retry_entity_workflow(
    deps: Dependencies,
    request: featurestore_v1_entity_workflow_service_pb2.RetryEntityWorkflowRequest
) -> featurestore_v1_entity_workflow_service_pb2.RetryEntityWorkflowResponse:
    """Retrys an entity."""
    response = featurestore_v1_entity_workflow_service_pb2.RetryEntityWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RetryEntityWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RetryEntityWorkflow', {'reason': request.reason})
        await deps.repository.save_entity(request.context.tenant_id, request.entity)
        response_0 = anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalResponse()
        response_1 = featurestore_v1_feature_view_reporting_service_pb2.StreamFeatureViewMetricsResponse()
        outgoing_0 = anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalRequest(
            context=request.context,
            details=anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
            ),
            detector=anomalies_v1_anomalies_pb2.Detector(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.entity.audit.updated_at)
            )
        )
        response_0 = await deps.clients.anomalies_detector_approval.CommentDetectorApproval(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_feature_view_reporting_service_pb2.StreamFeatureViewMetricsRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(
                email=response_0.detector.owner.email,
                name=request.details.notify.name
            )
        )
        async for chunk_1 in deps.clients.featurestore_feature_view_reporting.StreamFeatureViewMetrics(
            outgoing_1,
            timeout=deps.settings.timeout
        ):
            response_1 = chunk_1
        returned_0_0 = response_0.detector.audit.created_at
        if returned_0_0.ListFields():
            response.entity.audit.created_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.detector.audit.etag
        if returned_0_1:
            response.entity.audit.etag = returned_0_1
        echoed_0 = request.entity_id
        response.entity.entity_id = echoed_0
        echoed_1 = request.entity.name
        response.entity.contact.name.CopyFrom(echoed_1)
        return response


async def handle_start_entity_workflow(
    deps: Dependencies,
    request: featurestore_v1_entity_workflow_service_pb2.StartEntityWorkflowRequest
) -> featurestore_v1_entity_workflow_service_pb2.StartEntityWorkflowResponse:
    """Starts an entity."""
    response = featurestore_v1_entity_workflow_service_pb2.StartEntityWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('StartEntityWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'StartEntityWorkflow', {'reason': request.reason})
        await deps.repository.save_entity(request.context.tenant_id, request.entity)
        response_0 = metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportResponse()
        response_1 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityResponse()
        response_2 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertResponse()
        response_3 = lineage_v1_lineage_edge_reporting_service_pb2.ScheduleLineageEdgeReportResponse()
        outgoing_0 = metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest(
            context=request.context,
            details=metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest.Details(
                recipient=common_v1_contact_pb2.ContactInfo(
                    email=request.entity.contact.email,
                    name=request.details.notify.name,
                    phone=request.entity.contact.phone,
                    preferred_channel=request.details.notify.preferred_channel
                )
            )
        )
        response_0 = await deps.clients.metrics_metric_series_export.ShareMetricSeriesExport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        fields_1: dict[str, Any] = {
            'context': request.context,
            'dataset': {
                'dimensions': {'weight': response_0.metric_series.dimensions.weight},
                'owner': {'email': request.details.notify.email}
            }
        }
        outgoing_1 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest(**fields_1)
        response_1 = await deps.clients.datasets_dataset_validation.CheckDatasetEligibility(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertRequest()
        outgoing_2.context.CopyFrom(request.context)
        if response_1.dataset.WhichOneof('locator') == 'address':
            outgoing_2.details.destination.country_code = response_1.dataset.address.country_code
        outgoing_2.metric_alert.owner.user_id = response_1.dataset.owner.user_id
        response_2 = await deps.clients.metrics_metric_alert_validation.ScoreMetricAlert(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = lineage_v1_lineage_edge_reporting_service_pb2.ScheduleLineageEdgeReportRequest(
            annotations=dict(request.annotations),
            context=request.context,
            reason=response_2.metric_alert.block.reason
        )
        document_3 = MessageToJson(outgoing_3, preserving_proto_field_name=True)
        outgoing_3 = Parse(document_3, lineage_v1_lineage_edge_reporting_service_pb2.ScheduleLineageEdgeReportRequest())
        response_3 = await deps.clients.lineage_lineage_edge_reporting.ScheduleLineageEdgeReport(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.outcome.message = returned_0_1
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.result.correlation_id = returned_1_0
        returned_1_1 = response_1.dataset.address.lines
        response.entity.primary_address.lines.extend(returned_1_1)
        returned_2_0 = response_2.result.correlation_id
        if returned_2_0:
            response.result.correlation_id = returned_2_0
        returned_2_1 = response_2.metric_alert.owner.user_id
        if returned_2_1:
            response.entity.relationship_manager.user_id = returned_2_1
        returned_3_0 = response_3.result.correlation_id
        if returned_3_0:
            response.result.correlation_id = returned_3_0
        echoed_0 = request.entity_id
        response.entity.entity_id = echoed_0
        echoed_1 = request.entity.status
        response.entity.status = echoed_1
        return response
