"""Checks data shares against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator
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
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import consent_record_sync_service_pb2 as customers_v1_consent_record_sync_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2_grpc as datahub_v1_data_share_validation_service_pb2_grpc
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datasets.v1 import data_schema_approval_service_pb2 as datasets_v1_data_schema_approval_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.driverapp.v1 import driver_home_query_service_pb2 as driverapp_v1_driver_home_query_service_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.forecasting.v1 import scenario_workflow_service_pb2 as forecasting_v1_scenario_workflow_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.lineage.v1 import impact_approval_service_pb2 as lineage_v1_impact_approval_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.modelregistry.v1 import deployment_approval_service_pb2 as modelregistry_v1_deployment_approval_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.recommendations.v1 import (
    interaction_approval_service_pb2 as recommendations_v1_interaction_approval_service_pb2,
)

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import DataShareValidationCheckDataShareEligibility3Adapter
from acme_data.domains.datahub.adapters import DataShareValidationCheckDataShareEligibility3Port
from acme_data.domains.datahub.adapters import DataShareValidationValidateDataShare2Adapter
from acme_data.domains.datahub.adapters import DataShareValidationValidateDataShare2Port
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import DataShareValidationPreviewDataShare2Command
from acme_data.domains.datahub.models import DataShareValidationScoreDataShare0Command
from acme_data.domains.datahub.models import to_data_share_validation_preview_data_share2_command
from acme_data.domains.datahub.models import to_data_share_validation_score_data_share0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DataShareValidationServicer(datahub_v1_data_share_validation_service_pb2_grpc.DataShareValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckDataShareEligibility(
        self, request: datahub_v1_data_share_validation_service_pb2.CheckDataShareEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_validation_service_pb2.CheckDataShareEligibilityResponse:
        """Checks a data share."""
        return await self.handle_check_data_share_eligibility(request)

    @rpc_errors
    async def ExplainDataShareDecision(
        self, request: datahub_v1_data_share_validation_service_pb2.ExplainDataShareDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_validation_service_pb2.ExplainDataShareDecisionResponse:
        """Explains a data share."""
        return await self.handle_explain_data_share_decision(request)

    @rpc_errors
    async def LintDataShares(
        self, request: datahub_v1_data_share_validation_service_pb2.LintDataSharesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_validation_service_pb2.LintDataSharesResponse:
        """Lints a data share."""
        return await self.handle_lint_data_shares(request)

    @rpc_errors
    async def NormalizeDataShare(
        self, request: datahub_v1_data_share_validation_service_pb2.NormalizeDataShareRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_validation_service_pb2.NormalizeDataShareResponse:
        """Normalizes a data share."""
        return await self.handle_normalize_data_share(request)

    @rpc_errors
    async def PreviewDataShare(
        self, request: datahub_v1_data_share_validation_service_pb2.PreviewDataShareRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_validation_service_pb2.PreviewDataShareResponse:
        """Previews a data share."""
        return await self.handle_preview_data_share(request)

    @rpc_errors
    async def ScoreDataShare(
        self, request: datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_validation_service_pb2.ScoreDataShareResponse:
        """Scores a data share."""
        return await self.handle_score_data_share(request)

    @rpc_errors
    async def ValidateDataShare(
        self, request: datahub_v1_data_share_validation_service_pb2.ValidateDataShareRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_validation_service_pb2.ValidateDataShareResponse:
        """Validates a data share."""
        return await self.handle_validate_data_share(request)

    async def handle_check_data_share_eligibility(
        self,
        request: datahub_v1_data_share_validation_service_pb2.CheckDataShareEligibilityRequest
    ) -> datahub_v1_data_share_validation_service_pb2.CheckDataShareEligibilityResponse:
        """Checks a data share."""
        deps = self.deps
        response = datahub_v1_data_share_validation_service_pb2.CheckDataShareEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckDataShareEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckDataShareEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentResponse()
            response_1 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse()
            response_2 = customers_v1_consent_record_sync_service_pb2.PullConsentRecordsResponse()
            response_3 = featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagResponse()
            outgoing_0 = modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.data_share.audit.updated_by),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
                        )
                    ]
                ),
                details=modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=request.data_share.counterparty.display_name)
                )
            )
            send_0 = partial(
                deps.clients.modelregistry_deployment_approval.SubmitDeployment,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            outgoing_1 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.data_share.audit.created_at),
                    customer=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.data_share.counterparty.display_name
                    )
                )
            )
            response_1 = await hooks.data_share_validation_check_data_share_eligibility1(
                deps.clients.datahub_workspace_approval,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = customers_v1_consent_record_sync_service_pb2.PullConsentRecordsRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.consent_record.subject.display_name = request.data_share.counterparty.display_name
            outgoing_2.consent_record.correlation_id = response_1.result.correlation_id
            outgoing_2.annotations.update(dict(request.annotations))
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.customers_consent_record_sync.PullConsentRecords(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagRequest(
                context=request.context,
                details=featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        postal_code=response_0.deployment.location.postal_code
                    )
                ),
                feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.details.contact.email,
                        user_id=response_0.deployment.organizer.user_id
                    )
                )
            )
            port_3: DataShareValidationCheckDataShareEligibility3Port = DataShareValidationCheckDataShareEligibility3Adapter(
                deps.clients.featureflags_feature_flag_validation,
                deps.settings.timeout
            )
            response_3 = await port_3.execute(outgoing_3)
            returned_0_0 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_0)
            returned_1_0 = response_1.workspace.audit.created_by
            if returned_1_0:
                response.data_share.audit.created_by = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.outcome.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            returned_3_0 = response_3.feature_flag.discount.amount
            returned_3_0_part_1 = response.data_share.lines.add()
            if returned_3_0.ListFields():
                returned_3_0_part_1.tax.amount.MergeFrom(returned_3_0)
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.outcome.message = returned_3_1
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.billing_address
            response.data_share.billing_address.CopyFrom(echoed_1)
            return response

    async def handle_explain_data_share_decision(
        self,
        request: datahub_v1_data_share_validation_service_pb2.ExplainDataShareDecisionRequest
    ) -> datahub_v1_data_share_validation_service_pb2.ExplainDataShareDecisionResponse:
        """Explains a data share."""
        deps = self.deps
        response = datahub_v1_data_share_validation_service_pb2.ExplainDataShareDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainDataShareDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainDataShareDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = recommendations_v1_interaction_approval_service_pb2.ListPendingInteractionsResponse()
            response_1 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse()
            response_2 = modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalResponse()
            outgoing_0 = recommendations_v1_interaction_approval_service_pb2.ListPendingInteractionsRequest(
                context=request.context,
                filter=recommendations_v1_interaction_approval_service_pb2.ListPendingInteractionsRequest.Filter(
                    created_after=request.data_share.audit.updated_at,
                    region=request.data_share.billing_address.region
                )
            )
            outgoing_1 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.contact.email),
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.data_share.audit.etag),
                    requester=common_v1_contact_pb2.ContactInfo(name=request.details.contact.name)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.recommendations_interaction_approval.ListPendingInteractions(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.datahub_workspace_approval.DelegateWorkspaceApproval(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    location=common_v1_address_pb2.PostalAddress(region=request.data_share.billing_address.region),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=response_1.workspace.requester.email,
                                name=request.details.contact.name,
                                preferred_channel=response_1.workspace.requester.preferred_channel
                            )
                        )
                    ]
                )
            )
            response_2 = cast(modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalResponse, await deps.bus.request(
                'acme.datahub.v1.DataShareValidationService/ExplainDataShareDecision/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.workspace.audit.created_at
            if returned_1_0.ListFields():
                response.data_share.audit.created_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.workspace.audit.created_by
            if returned_1_1:
                response.data_share.audit.created_by = returned_1_1
            returned_2_0 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_0)
            returned_2_1 = response_2.deployment.audit.created_at
            if returned_2_1.ListFields():
                response.data_share.audit.created_at.MergeFrom(returned_2_1)
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.due_at
            response.data_share.due_at.CopyFrom(echoed_1)
            return response

    async def handle_lint_data_shares(
        self,
        request: datahub_v1_data_share_validation_service_pb2.LintDataSharesRequest
    ) -> datahub_v1_data_share_validation_service_pb2.LintDataSharesResponse:
        """Lints a data share."""
        deps = self.deps
        response = datahub_v1_data_share_validation_service_pb2.LintDataSharesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintDataShares', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintDataShares', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse()
            response_1 = metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    audit=common_v1_audit_pb2.AuditInfo(
                        updated_at=request.data_share.audit.updated_at,
                        updated_by=request.data_share.audit.updated_by
                    ),
                    comments=[datahub_v1_datahub_pb2.WorkspaceComment(created_at=request.data_share.audit.created_at)]
                )
            )
            response_0 = await deps.clients.datahub_workspace_approval.ApproveWorkspace(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesRequest(
                context=request.context,
                details=metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=response_0.workspace.assignee.email,
                        name=request.details.contact.name,
                        phone=response_0.workspace.requester.phone
                    )
                )
            )
            method_name_1 = 'UnsubscribeDashboardUpdates'
            response_1 = await getattr(
                deps.clients.metrics_dashboard_notification,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.workspace.audit.created_by
            if returned_0_0:
                response.data_share.audit.created_by = returned_0_0
            returned_1_0 = response_1.dashboard.billing_address.country_code
            if returned_1_0:
                response.data_share.billing_address.country_code = returned_1_0
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.metadata
            response.data_share.metadata.update(echoed_1)
            return response

    async def handle_normalize_data_share(
        self,
        request: datahub_v1_data_share_validation_service_pb2.NormalizeDataShareRequest
    ) -> datahub_v1_data_share_validation_service_pb2.NormalizeDataShareResponse:
        """Normalizes a data share."""
        deps = self.deps
        response = datahub_v1_data_share_validation_service_pb2.NormalizeDataShareResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeDataShare', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeDataShare', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = forecasting_v1_scenario_workflow_service_pb2.AdvanceScenarioWorkflowResponse()
            response_1 = driverapp_v1_driver_home_query_service_pb2.FindDriverHomesResponse()
            response_2 = lineage_v1_impact_approval_service_pb2.RecallImpactResponse()
            response_3 = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'scenario': {
                    'audit': {
                        'created_at': request.data_share.audit.created_at,
                        'updated_by': request.data_share.audit.updated_by
                    },
                    'requester': {'email': request.details.contact.email, 'phone': request.details.contact.phone}
                }
            }
            outgoing_0 = forecasting_v1_scenario_workflow_service_pb2.AdvanceScenarioWorkflowRequest(**fields_0)
            response_0 = await deps.clients.forecasting_scenario_workflow.AdvanceScenarioWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = driverapp_v1_driver_home_query_service_pb2.FindDriverHomesRequest(
                context=request.context,
                filter=driverapp_v1_driver_home_query_service_pb2.FindDriverHomesRequest.Filter(
                    region=request.data_share.billing_address.region
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, driverapp_v1_driver_home_query_service_pb2.FindDriverHomesRequest())
            response_1 = await deps.clients.driverapp_driver_home_query.FindDriverHomes(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_impact_approval_service_pb2.RecallImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=response_0.scenario.assignee.display_name),
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.scenario.audit.updated_by),
                    customer=customers_v1_refs_pb2.CustomerRef(email=response_0.scenario.requester.email)
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, lineage_v1_impact_approval_service_pb2.RecallImpactRequest())
            response_2 = await deps.clients.lineage_impact_approval.RecallImpact(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.workspace.channel.channel = response_2.impact.channel.channel
            outgoing_3.workspace.requester.phone = request.details.contact.phone
            outgoing_3.workspace.audit.created_at.CopyFrom(request.data_share.audit.created_at)
            merged_3 = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.datahub_workspace_approval.SubmitWorkspace(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.scenario.audit.created_by
            if returned_0_0:
                response.data_share.audit.created_by = returned_0_0
            returned_0_1 = response_0.scenario.audit.etag
            if returned_0_1:
                response.data_share.audit.etag = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.outcome.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.total
            response.data_share.total.CopyFrom(echoed_1)
            return response

    async def handle_preview_data_share(
        self,
        request: datahub_v1_data_share_validation_service_pb2.PreviewDataShareRequest
    ) -> datahub_v1_data_share_validation_service_pb2.PreviewDataShareResponse:
        """Previews a data share."""
        deps = self.deps
        response = datahub_v1_data_share_validation_service_pb2.PreviewDataShareResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewDataShare', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewDataShare', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsResponse()
            response_1 = modelregistry_v1_deployment_approval_service_pb2.RejectDeploymentResponse()
            response_2 = featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityResponse()
            outgoing_0 = ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsRequest.Filter(
                    created_after=request.data_share.audit.created_at,
                    region=request.data_share.billing_address.region
                )
            )
            outgoing_1 = modelregistry_v1_deployment_approval_service_pb2.RejectDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                preferred_channel=request.details.contact.preferred_channel
                            )
                        )
                    ]
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.ledger_ledger_account_query.BrowseLedgerAccounts(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.modelregistry_deployment_approval.RejectDeployment(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            command_2 = DataShareValidationPreviewDataShare2Command(
                context=request.context,
                feature_flag_audit_etag=response_1.deployment.audit.etag
            )
            outgoing_2 = to_data_share_validation_preview_data_share2_command(command_2)
            response_2 = await deps.clients.featureflags_feature_flag_validation.CheckFeatureFlagEligibility(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.feature_flag.description
            returned_2_0_part_1 = response.data_share.lines.add()
            if returned_2_0:
                returned_2_0_part_1.description = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.number
            response.data_share.number = echoed_1
            return response

    async def handle_score_data_share(
        self,
        request: datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest
    ) -> datahub_v1_data_share_validation_service_pb2.ScoreDataShareResponse:
        """Scores a data share."""
        deps = self.deps
        response = datahub_v1_data_share_validation_service_pb2.ScoreDataShareResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreDataShare', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreDataShare', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse()
            response_1 = datasets_v1_data_schema_approval_service_pb2.ApproveDataSchemaResponse()
            command_0 = DataShareValidationScoreDataShare0Command.model_validate(
                {
                    'context': request.context,
                    'workspace_customer_display_name': request.data_share.counterparty.display_name
                }
            )
            outgoing_0 = to_data_share_validation_score_data_share0_command(command_0)
            response_0 = await deps.clients.datahub_workspace_approval.ApproveWorkspace(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            requests_1: list[datasets_v1_data_schema_approval_service_pb2.ApproveDataSchemaRequest] = []
            for item_1 in request.data_share.lines:
                outgoing_1 = datasets_v1_data_schema_approval_service_pb2.ApproveDataSchemaRequest(
                    context=request.context,
                    data_schema=datasets_v1_datasets_pb2.DataSchema(
                        children=[
                            datasets_v1_datasets_pb2.DataSchema(
                                children=[
                                    datasets_v1_datasets_pb2.DataSchema(
                                        attributes=dict(item_1.attributes),
                                        location=common_v1_address_pb2.PostalAddress(
                                            recipient=request.details.destination.recipient
                                        ),
                                        manager=identity_v1_refs_pb2.UserRef(email=response_0.workspace.assignee.email)
                                    )
                                ]
                            )
                        ]
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.datasets_data_schema_approval.ApproveDataSchema(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.workspace.audit.updated_at
            if returned_0_1.ListFields():
                response.data_share.audit.updated_at.MergeFrom(returned_0_1)
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.status
            response.data_share.status = echoed_1
            return response

    async def handle_validate_data_share(
        self,
        request: datahub_v1_data_share_validation_service_pb2.ValidateDataShareRequest
    ) -> datahub_v1_data_share_validation_service_pb2.ValidateDataShareResponse:
        """Validates a data share."""
        deps = self.deps
        response = datahub_v1_data_share_validation_service_pb2.ValidateDataShareResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateDataShare', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateDataShare', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceResponse()
            response_1 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse()
            response_2 = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceRequest(
                context=request.context,
                details=datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=request.data_share.counterparty.display_name)
                ),
                workspace=datahub_v1_datahub_pb2.Workspace(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.data_share.audit.created_at,
                        created_by=request.data_share.audit.created_by
                    ),
                    requester=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
                )
            )
            response_0 = await hooks.data_share_validation_validate_data_share0(
                deps.clients.datahub_workspace_approval,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.workspace.customer.email = response_0.workspace.assignee.email
            if response_0.workspace.WhichOneof('origin') == 'customer':
                outgoing_1.workspace.assignee.display_name = response_0.workspace.customer.display_name
            outgoing_1.details.approver.user_id = response_0.workspace.assignee.user_id
            field_1_4_part_1 = outgoing_1.workspace.comments.add()
            field_1_4_part_1.created_at.CopyFrom(response_0.workspace.audit.created_at)
            response_1 = await deps.clients.datahub_workspace_approval.ApproveWorkspace(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    comments=[datahub_v1_datahub_pb2.WorkspaceComment(created_at=response_0.workspace.audit.created_at)]
                )
            )
            port_2: DataShareValidationValidateDataShare2Port = DataShareValidationValidateDataShare2Adapter(
                deps.clients.datahub_workspace_approval,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.workspace.customer.display_name
            if returned_0_0:
                response.data_share.counterparty.display_name = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.workspace.audit.updated_at
            if returned_1_0.ListFields():
                response.data_share.audit.updated_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.workspace.customer.display_name
            if returned_1_1:
                response.data_share.counterparty.display_name = returned_1_1
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.status
            response.data_share.status = echoed_1
            return response
