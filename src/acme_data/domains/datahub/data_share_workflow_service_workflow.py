"""Application workflow for DataShare Workflow."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage

from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_import_service_pb2 as customers_v1_preference_import_service_pb2
from acme.customers.v1 import preference_sync_service_pb2 as customers_v1_preference_sync_service_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_reporting_service_pb2 as datahub_v1_data_share_reporting_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import data_share_workflow_service_pb2 as datahub_v1_data_share_workflow_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import refs_pb2 as datahub_v1_refs_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_integration_service_pb2 as datahub_v1_workspace_integration_service_pb2
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.labeling.v1 import annotation_approval_service_pb2_grpc as labeling_v1_annotation_approval_service_pb2_grpc
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_lifecycle_service_pb2 as modelregistry_v1_registered_model_lifecycle_service_pb2,
)
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import DataShareWorkflowSignalDataShareWorkflow0Adapter
from acme_data.domains.datahub.adapters import DataShareWorkflowSignalDataShareWorkflow0Port
from acme_data.domains.datahub.adapters import DataShareWorkflowSignalDataShareWorkflow2Adapter
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import DataShareWorkflowResumeDataShareWorkflow1Command
from acme_data.domains.datahub.models import to_data_share_workflow_resume_data_share_workflow1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DataShareWorkflowServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_advance_data_share_workflow(
        self,
        request: datahub_v1_data_share_workflow_service_pb2.AdvanceDataShareWorkflowRequest
    ) -> datahub_v1_data_share_workflow_service_pb2.AdvanceDataShareWorkflowResponse:
        """Advances a data share."""
        deps = self.deps
        response = datahub_v1_data_share_workflow_service_pb2.AdvanceDataShareWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceDataShareWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceDataShareWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse()
            response_1 = datahub_v1_data_share_approval_service_pb2.EscalateDataShareResponse()
            response_2 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse()
            outgoing_0 = featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=request.data_share.billing_address.postal_code,
                        recipient=request.data_share.billing_address.recipient
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.data_share.audit.created_at,
                        created_by=request.data_share.audit.created_by
                    )
                )
            )
            outgoing_1 = datahub_v1_data_share_approval_service_pb2.EscalateDataShareRequest(
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    counterparty=datahub_v1_refs_pb2.NotebookRef(number=request.data_share.counterparty.number)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.featurestore_feature_view_sync.ReconcileFeatureViews(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.datahub_data_share_approval.EscalateDataShare(outgoing_1, timeout=deps.settings.timeout),
            )
            outgoing_2 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.notify.email),
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.data_share.audit.created_at,
                        etag=response_0.feature_view.audit.etag,
                        updated_at=request.data_share.audit.updated_at
                    )
                )
            )
            response_2 = cast(datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse, await deps.bus.request(
                'acme.datahub.v1.DataShareWorkflowService/AdvanceDataShareWorkflow/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.data_share.number
            if returned_1_0:
                response.data_share.number = returned_1_0
            returned_1_1 = response_1.data_share.billing_address
            if returned_1_1.ListFields():
                response.data_share.billing_address.MergeFrom(returned_1_1)
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.issued_at
            response.data_share.issued_at.CopyFrom(echoed_1)
            return response

    async def handle_cancel_data_share_workflow(
        self,
        request: datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowRequest
    ) -> datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowResponse:
        """Cancels a data share."""
        deps = self.deps
        response = datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelDataShareWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelDataShareWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackResponse()
            response_1 = customers_v1_preference_import_service_pb2.ValidatePreferenceImportResponse()
            response_2 = modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest(
                context=request.context,
                details=anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                )
            )
            response_0 = await deps.clients.anomalies_anomaly_feedback_approval.EscalateAnomalyFeedback(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_preference_import_service_pb2.ValidatePreferenceImportRequest(
                context=request.context,
                details=customers_v1_preference_import_service_pb2.ValidatePreferenceImportRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                ),
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.data_share.audit.created_at,
                        created_by=request.data_share.audit.created_by
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.data_share.counterparty.display_name)
                )
            )
            method_name_1 = 'ValidatePreferenceImport'
            response_1 = await getattr(
                deps.clients.customers_preference_import,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            callbacks_2: list[
                Callable[
                    [],
                    Awaitable[
                        modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryResponse
                    ]
                ]
            ] = []
            for item_2 in request.data_share.lines:
                outgoing_2 = modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryRequest(
                    context=request.context,
                    registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                        components={
                            'primary': modelregistry_v1_modelregistry_pb2.RegisteredModelComponent(
                                description=item_2.description
                            )
                        }
                    )
                )
                async def send_2(
                    payload: modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryRequest = outgoing_2
                ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryResponse:
                    return await deps.clients.modelregistry_registered_model_lifecycle.ScheduleRegisteredModelExpiry(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_2.append(send_2)
            for callback_2 in callbacks_2:
                response_2 = await callback_2()
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.preference.discount.amount
            returned_1_1_part_1 = response.data_share.lines.add()
            if returned_1_1.ListFields():
                returned_1_1_part_1.tax.amount.MergeFrom(returned_1_1)
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.due_at
            response.data_share.due_at.CopyFrom(echoed_1)
            return response

    async def handle_inspect_data_share_workflow(
        self,
        request: datahub_v1_data_share_workflow_service_pb2.InspectDataShareWorkflowRequest
    ) -> datahub_v1_data_share_workflow_service_pb2.InspectDataShareWorkflowResponse:
        """Returns a data share."""
        deps = self.deps
        response = datahub_v1_data_share_workflow_service_pb2.InspectDataShareWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectDataShareWorkflow', extra={'fields': {'domain': 'datahub'}})
            await deps.repository.audit(request.context.tenant_id, 'InspectDataShareWorkflow', {})
            response_0 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalResponse()
            outgoing_0 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest(
                context=request.context,
                details=datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.datahub_notebook_approval.DelegateNotebookApproval(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.notebook.audit.updated_by
            if returned_0_0:
                response.data_share.audit.updated_by = returned_0_0
            returned_0_1 = response_0.notebook.billing_address.recipient
            if returned_0_1:
                response.data_share.billing_address.recipient = returned_0_1
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            return response

    async def handle_list_data_share_workflows(
        self,
        request: datahub_v1_data_share_workflow_service_pb2.ListDataShareWorkflowsRequest
    ) -> datahub_v1_data_share_workflow_service_pb2.ListDataShareWorkflowsResponse:
        """Lists data shares a page at a time."""
        deps = self.deps
        response = datahub_v1_data_share_workflow_service_pb2.ListDataShareWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListDataShareWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListDataShareWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportResponse()
            outgoing_0 = pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_step_export.SharePipelineStepExport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline_step.owner.display_name
            returned_0_0_part_0 = response.data_shares.add()
            if returned_0_0:
                returned_0_0_part_0.counterparty.display_name = returned_0_0
            return response

    async def handle_pause_data_share_workflow(
        self,
        request: datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowRequest
    ) -> datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowResponse:
        """Pauses a data share."""
        deps = self.deps
        response = datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseDataShareWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PauseDataShareWorkflow', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse()
            response_1 = datahub_v1_data_share_approval_service_pb2.CommentDataShareApprovalResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.workspace.comments.add()
            field_0_1_part_1.created_at.CopyFrom(request.data_share.audit.created_at)
            merged_0 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.datahub_workspace_approval.EscalateWorkspace(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_data_share_approval_service_pb2.CommentDataShareApprovalRequest(
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    counterparty=datahub_v1_refs_pb2.NotebookRef(number=request.data_share.counterparty.number)
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = datahub_v1_data_share_approval_service_pb2.CommentDataShareApprovalRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.datahub_data_share_approval.CommentDataShareApproval(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.workspace.customer.display_name
            if returned_0_1:
                response.data_share.counterparty.display_name = returned_0_1
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.notes
            response.data_share.notes = echoed_1
            return response

    async def handle_resume_data_share_workflow(
        self,
        request: datahub_v1_data_share_workflow_service_pb2.ResumeDataShareWorkflowRequest
    ) -> datahub_v1_data_share_workflow_service_pb2.ResumeDataShareWorkflowResponse:
        """Resumes a data share."""
        deps = self.deps
        response = datahub_v1_data_share_workflow_service_pb2.ResumeDataShareWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeDataShareWorkflow', extra={'fields': {'data_share_id': request.data_share.data_share_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeDataShareWorkflow',
                {'data_share_id': request.data_share.data_share_id}
            )
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = labeling_v1_annotation_approval_service_pb2.ApproveAnnotationResponse()
            response_1 = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse()
            outgoing_0 = labeling_v1_annotation_approval_service_pb2.ApproveAnnotationRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(
                        display_name=request.data_share.counterparty.display_name
                    )
                ),
                context=request.context,
                details=labeling_v1_annotation_approval_service_pb2.ApproveAnnotationRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                ),
                reason=request.reason
            )
            registered_0 = cast(
                labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub,
                deps.clients.registry['acme.labeling.v1.AnnotationApprovalService']
            )
            response_0 = await registered_0.ApproveAnnotation(outgoing_0, timeout=deps.settings.timeout)
            command_1 = DataShareWorkflowResumeDataShareWorkflow1Command(
                context=request.context,
                workspace_requester_preferred_channel=request.details.notify.preferred_channel,
                workspace_assignee_display_name=request.data_share.counterparty.display_name,
                workspace_audit_etag=request.data_share.audit.etag
            )
            outgoing_1 = to_data_share_workflow_resume_data_share_workflow1_command(command_1)
            response_1 = await deps.clients.datahub_workspace_approval.RecallWorkspace(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.annotation.subject.display_name
            if returned_0_1:
                response.data_share.counterparty.display_name = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.workspace.audit.created_at
            if returned_1_1.ListFields():
                response.data_share.audit.created_at.MergeFrom(returned_1_1)
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.number
            response.data_share.counterparty.number = echoed_1
            return response

    async def handle_retry_data_share_workflow(
        self,
        request: datahub_v1_data_share_workflow_service_pb2.RetryDataShareWorkflowRequest
    ) -> datahub_v1_data_share_workflow_service_pb2.RetryDataShareWorkflowResponse:
        """Retrys a data share."""
        deps = self.deps
        response = datahub_v1_data_share_workflow_service_pb2.RetryDataShareWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryDataShareWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RetryDataShareWorkflow', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = datahub_v1_data_share_reporting_service_pb2.CountDataShareTotalsResponse()
            response_1 = datahub_v1_data_share_reporting_service_pb2.StreamDataShareMetricsResponse()
            response_2 = customers_v1_preference_sync_service_pb2.ResolvePreferenceConflictResponse()
            response_3 = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventResponse()
            async for item_0 in async_messages(request.data_share.lines):
                outgoing_0 = datahub_v1_data_share_reporting_service_pb2.CountDataShareTotalsRequest(
                    context=request.context,
                    filter=datahub_v1_data_share_reporting_service_pb2.CountDataShareTotalsRequest.Filter(
                        labels=dict(item_0.attributes),
                        owner_id=item_0.line_id,
                        region=request.data_share.billing_address.region
                    )
                )
                response_0 = await deps.clients.datahub_data_share_reporting.CountDataShareTotals(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = datahub_v1_data_share_reporting_service_pb2.StreamDataShareMetricsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.details.notify.email,
                    name=request.details.notify.name,
                    phone=request.details.notify.phone
                )
            )
            async for chunk_1 in deps.clients.datahub_data_share_reporting.StreamDataShareMetrics(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = customers_v1_preference_sync_service_pb2.ResolvePreferenceConflictRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.data_share.audit.etag,
                        updated_at=request.data_share.audit.updated_at
                    )
                )
            )
            response_2 = await hooks.data_share_workflow_retry_data_share_workflow2(
                deps.clients.customers_preference_sync,
                outgoing_2,
                deps.settings.timeout
            )
            outgoing_3 = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.reason = response_2.preference.block.reason
            outgoing_3.annotations.update(dict(request.annotations))
            outgoing_3.details.message_id = response_0.result.message
            outgoing_3.context.tenant_id = tenant_id.get()
            response_3 = await deps.clients.datahub_workspace_integration.AcknowledgeWorkspaceEvent(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.workspace.audit.etag
            if returned_3_0:
                response.data_share.audit.etag = returned_3_0
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.status
            response.data_share.status = echoed_1
            return response

    async def handle_signal_data_share_workflow(
        self,
        request: datahub_v1_data_share_workflow_service_pb2.SignalDataShareWorkflowRequest
    ) -> datahub_v1_data_share_workflow_service_pb2.SignalDataShareWorkflowResponse:
        """Signals a data share."""
        deps = self.deps
        response = datahub_v1_data_share_workflow_service_pb2.SignalDataShareWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalDataShareWorkflow', extra={'fields': {'notes': request.data_share.notes}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalDataShareWorkflow',
                {'notes': request.data_share.notes}
            )
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = datahub_v1_data_share_reporting_service_pb2.DeleteDataShareReportResponse()
            response_1 = datahub_v1_data_share_validation_service_pb2.PreviewDataShareResponse()
            response_2 = datahub_v1_notebook_approval_service_pb2.RejectNotebookResponse()
            outgoing_0 = datahub_v1_data_share_reporting_service_pb2.DeleteDataShareReportRequest(
                context=request.context,
                data_share_id=request.data_share.data_share_id,
                etag=request.data_share.audit.etag,
                reason=request.reason
            )
            port_0: DataShareWorkflowSignalDataShareWorkflow0Port = DataShareWorkflowSignalDataShareWorkflow0Adapter(
                deps.clients.datahub_data_share_reporting,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = datahub_v1_data_share_validation_service_pb2.PreviewDataShareRequest(
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.data_share.audit.created_at),
                    card=datahub_v1_datahub_pb2.DataShareCardSettlement(network=request.data_share.card.network),
                    counterparty=datahub_v1_refs_pb2.NotebookRef(number=request.data_share.counterparty.number)
                ),
                details=datahub_v1_data_share_validation_service_pb2.PreviewDataShareRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                )
            )
            steps_1 = [
                partial(
                    deps.clients.datahub_data_share_validation.PreviewDataShare,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = datahub_v1_notebook_approval_service_pb2.RejectNotebookRequest(
                context=request.context,
                details=datahub_v1_notebook_approval_service_pb2.RejectNotebookRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=request.data_share.counterparty.display_name)
                ),
                notebook=datahub_v1_datahub_pb2.Notebook(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.data_share.audit.created_at,
                        etag=response_1.data_share.audit.etag
                    ),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=response_1.data_share.billing_address.country_code
                    )
                )
            )
            response_2 = await DataShareWorkflowSignalDataShareWorkflow2Adapter(
                deps.clients.datahub_notebook_approval,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.data_share.counterparty
            if returned_1_0.ListFields():
                response.data_share.counterparty.MergeFrom(returned_1_0)
            returned_1_1 = response_1.data_share.audit.updated_by
            if returned_1_1:
                response.data_share.audit.updated_by = returned_1_1
            returned_2_0 = response_2.notebook.audit.etag
            if returned_2_0:
                response.data_share.audit.etag = returned_2_0
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.status
            response.data_share.status = echoed_1
            return response

    async def handle_start_data_share_workflow(
        self,
        request: datahub_v1_data_share_workflow_service_pb2.StartDataShareWorkflowRequest
    ) -> datahub_v1_data_share_workflow_service_pb2.StartDataShareWorkflowResponse:
        """Starts a data share."""
        deps = self.deps
        response = datahub_v1_data_share_workflow_service_pb2.StartDataShareWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartDataShareWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'StartDataShareWorkflow', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = datahub_v1_notebook_workflow_service_pb2.ResumeNotebookWorkflowResponse()
            response_1 = modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsResponse()
            response_2 = datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowResponse()
            outgoing_0 = datahub_v1_notebook_workflow_service_pb2.ResumeNotebookWorkflowRequest(
                context=request.context,
                details=datahub_v1_notebook_workflow_service_pb2.ResumeNotebookWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                )
            )
            response_0 = cast(datahub_v1_notebook_workflow_service_pb2.ResumeNotebookWorkflowResponse, await deps.bus.request(
                'acme.datahub.v1.DataShareWorkflowService/StartDataShareWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            for item_1 in request.data_share.attachments:
                outgoing_1 = modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsRequest(
                    context=request.context,
                    deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                        audit=common_v1_audit_pb2.AuditInfo(etag=response_0.notebook.audit.etag),
                        location=common_v1_address_pb2.PostalAddress(
                            lines=list(response_0.notebook.billing_address.lines)
                        )
                    ),
                    details=modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsRequest.Details(
                        checksum=item_1.checksum
                    )
                )
                response_1 = await deps.clients.modelregistry_deployment_sync.PullDeployments(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            requests_2: list[datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowRequest] = []
            for item_2 in request.data_share.lines:
                outgoing_2 = datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowRequest(
                    context=request.context,
                    notebook=datahub_v1_datahub_pb2.Notebook(
                        lines=[
                            datahub_v1_datahub_pb2.NotebookLine(
                                amount=item_2.tax.amount,
                                attributes=dict(item_2.attributes),
                                tax=datahub_v1_datahub_pb2.NotebookLineTax(
                                    exemptions=list(item_2.tax.exemptions),
                                    rate=item_2.tax.rate
                                )
                            )
                        ]
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.datahub_notebook_workflow.SignalNotebookWorkflow(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            returned_0_0 = response_0.notebook.billing_address
            if returned_0_0.ListFields():
                response.data_share.billing_address.MergeFrom(returned_0_0)
            returned_0_1 = response_0.notebook.audit.updated_by
            if returned_0_1:
                response.data_share.audit.updated_by = returned_0_1
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.status
            response.data_share.status = echoed_1
            return response
