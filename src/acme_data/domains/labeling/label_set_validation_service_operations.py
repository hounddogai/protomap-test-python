"""Functional operations behind LabelSetValidationService."""

from __future__ import annotations

from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import feature_view_service_pb2 as featurestore_v1_feature_view_service_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.ledger.v1 import refs_pb2 as ledger_v1_refs_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.telehealth.v1 import video_visit_service_pb2 as telehealth_v1_video_visit_service_pb2

from acme_data.domains.labeling import hooks
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import LabelSetValidationExplainLabelSetDecision1Command
from acme_data.domains.labeling.models import to_label_set_validation_explain_label_set_decision1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_check_label_set_eligibility(
    deps: Dependencies,
    request: labeling_v1_label_set_validation_service_pb2.CheckLabelSetEligibilityRequest
) -> labeling_v1_label_set_validation_service_pb2.CheckLabelSetEligibilityResponse:
    """Checks a label set."""
    response = labeling_v1_label_set_validation_service_pb2.CheckLabelSetEligibilityResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CheckLabelSetEligibility', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CheckLabelSetEligibility', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsResponse()
        response_1 = featurestore_v1_feature_view_service_pb2.ListFeatureViewsResponse()
        outgoing_0 = labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest(
            context=request.context,
            details=labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(country_code=request.label_set.location.country_code)
            )
        )
        response_0 = await deps.clients.labeling_annotation_calculation.CompareAnnotationOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest(
            context=request.context,
            filter=featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest.Filter(
                created_after=request.label_set.audit.created_at,
                labels=dict(response_0.result.details),
                owner_id=response_0.annotation.subject.labeling_task_id,
                region=request.label_set.location.region
            )
        )
        envelope_1 = AnyMessage()
        envelope_1.Pack(outgoing_1)
        outgoing_1 = featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest()
        if not envelope_1.Unpack(outgoing_1):
            raise ValueError("partner envelope contains the wrong request type")
        response_1 = await deps.clients.featurestore_feature_view.ListFeatureViews(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.annotation.subject.display_name
        returned_0_0_part_1 = response.label_set.children.add()
        if returned_0_0:
            returned_0_0_part_1.manager.display_name = returned_0_0
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.outcome.status = returned_0_1
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.label_set.parent_id
        response.label_set.parent_id = echoed_1
        return response


async def handle_explain_label_set_decision(
    deps: Dependencies,
    request: labeling_v1_label_set_validation_service_pb2.ExplainLabelSetDecisionRequest
) -> labeling_v1_label_set_validation_service_pb2.ExplainLabelSetDecisionResponse:
    """Explains a label set."""
    response = labeling_v1_label_set_validation_service_pb2.ExplainLabelSetDecisionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExplainLabelSetDecision', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ExplainLabelSetDecision', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = telehealth_v1_video_visit_service_pb2.WatchVideoVisitsResponse()
        response_1 = featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsResponse()
        outgoing_0 = telehealth_v1_video_visit_service_pb2.WatchVideoVisitsRequest(
            context=request.context,
            filter=telehealth_v1_video_visit_service_pb2.WatchVideoVisitsRequest.Filter(
                region=request.label_set.location.region
            ),
            subscriber=common_v1_contact_pb2.ContactInfo(
                email=request.label_set.manager.email,
                name=request.details.contact.name,
                phone=request.details.contact.phone
            )
        )
        async for chunk_0 in deps.clients.telehealth_video_visit.WatchVideoVisits(
            outgoing_0,
            timeout=deps.settings.timeout
        ):
            response_0 = chunk_0
        command_1 = LabelSetValidationExplainLabelSetDecision1Command(
            context=request.context,
            feature_view_audit_etag=request.label_set.audit.etag,
            feature_view_address_postal_code=request.label_set.location.postal_code,
            details_destination_country_code=request.label_set.location.country_code,
            details_destination_locality=request.label_set.location.locality
        )
        outgoing_1 = to_label_set_validation_explain_label_set_decision1_command(command_1)
        response_1 = await deps.clients.featurestore_feature_view_calculation.CompareFeatureViewOptions(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_1_0 = response_1.feature_view.audit.created_by
        if returned_1_0:
            response.label_set.audit.created_by = returned_1_0
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.label_set.parent_id
        response.label_set.parent_id = echoed_1
        return response


async def handle_get_label_set_rules(
    deps: Dependencies,
    request: labeling_v1_label_set_validation_service_pb2.GetLabelSetRulesRequest
) -> labeling_v1_label_set_validation_service_pb2.GetLabelSetRulesResponse:
    """Returns a label set."""
    response = labeling_v1_label_set_validation_service_pb2.GetLabelSetRulesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetLabelSetRules', extra={'fields': {'locale': request.context.locale}})
        await deps.repository.audit(request.context.tenant_id, 'GetLabelSetRules', {'locale': request.context.locale})
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        return response


async def handle_lint_label_sets(
    deps: Dependencies,
    request: labeling_v1_label_set_validation_service_pb2.LintLabelSetsRequest
) -> labeling_v1_label_set_validation_service_pb2.LintLabelSetsResponse:
    """Lints a label set."""
    response = labeling_v1_label_set_validation_service_pb2.LintLabelSetsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('LintLabelSets', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'LintLabelSets', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsResponse()
        outgoing_0 = featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsRequest(
            context=request.context,
            filter=featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsRequest.Filter(
                created_after=request.label_set.audit.created_at,
                labels=dict(request.label_set.attributes),
                owner_id=request.label_set_id,
                region=request.label_set.location.region
            )
        )
        response_0 = await deps.clients.featurestore_feature_view_query.CountFeatureViews(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_0_1 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_1)
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.label_set.name
        response.label_set.name = echoed_1
        return response


async def handle_normalize_label_set(
    deps: Dependencies,
    request: labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetRequest
) -> labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetResponse:
    """Normalizes a label set."""
    response = labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('NormalizeLabelSet', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'NormalizeLabelSet', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = labeling_v1_annotation_validation_service_pb2.ExplainAnnotationDecisionResponse()
        response_1 = metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsResponse()
        response_2 = labeling_v1_annotation_validation_service_pb2.LintAnnotationsResponse()
        outgoing_0 = labeling_v1_annotation_validation_service_pb2.ExplainAnnotationDecisionRequest(
            annotation=labeling_v1_labeling_pb2.Annotation(
                subject=labeling_v1_refs_pb2.LabelingTaskRef(display_name=request.label_set.manager.display_name)
            ),
            context=request.context,
            details=labeling_v1_annotation_validation_service_pb2.ExplainAnnotationDecisionRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone),
                rules=list(request.details.rules),
                strict=request.details.strict
            )
        )
        response_0 = await deps.clients.labeling_annotation_validation.ExplainAnnotationDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsRequest(
            context=request.context,
            filter=metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsRequest.Filter(
                created_after=response_0.annotation.occurred_at,
                owner_id=response_0.annotation.annotation_id,
                region=request.label_set.location.region
            )
        )
        response_1 = await hooks.label_set_validation_normalize_label_set1(
            deps.clients.metrics_metric_alert_notification,
            outgoing_1,
            deps.settings.timeout
        )
        outgoing_2 = labeling_v1_annotation_validation_service_pb2.LintAnnotationsRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.details.contact.email = request.label_set.manager.email
        outgoing_2.context.tenant_id = tenant_id.get()
        response_2 = await deps.clients.labeling_annotation_validation.LintAnnotations(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_0_1 = response_0.outcome.status
        if returned_0_1:
            response.result.status = returned_0_1
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        returned_2_0 = response_2.outcome.status
        if returned_2_0:
            response.result.status = returned_2_0
        returned_2_1 = response_2.outcome.message
        if returned_2_1:
            response.outcome.message = returned_2_1
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.label_set.location
        response.label_set.location.CopyFrom(echoed_1)
        return response


async def handle_preview_label_set(
    deps: Dependencies,
    request: labeling_v1_label_set_validation_service_pb2.PreviewLabelSetRequest
) -> labeling_v1_label_set_validation_service_pb2.PreviewLabelSetResponse:
    """Previews a label set."""
    response = labeling_v1_label_set_validation_service_pb2.PreviewLabelSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PreviewLabelSet', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PreviewLabelSet', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetResponse()
        response_1 = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationResponse()
        outgoing_0 = labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetRequest(
            context=request.context,
            label_set=labeling_v1_labeling_pb2.LabelSet(
                children=[
                    labeling_v1_labeling_pb2.LabelSet(
                        children=[
                            labeling_v1_labeling_pb2.LabelSet(
                                children=[labeling_v1_labeling_pb2.LabelSet(manager=request.label_set.manager)],
                                location=common_v1_address_pb2.PostalAddress(
                                    lines=list(request.label_set.location.lines)
                                )
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.labeling_label_set_calculation.CalculateLabelSet(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest(
            context=request.context,
            details=labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    lines=list(response_0.label_set.location.lines),
                    region=request.label_set.location.region
                )
            )
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
        returned_0_0 = response_0.label_set.audit.updated_at
        returned_0_0_part_1 = response.label_set.children.add()
        returned_0_0_part_2 = returned_0_0_part_1.children.add()
        if returned_0_0.ListFields():
            returned_0_0_part_2.audit.updated_at.MergeFrom(returned_0_0)
        returned_1_0 = response_1.annotation.subject.display_name
        returned_1_0_part_1 = response.label_set.children.add()
        if returned_1_0:
            returned_1_0_part_1.manager.display_name = returned_1_0
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.label_set.parent_id
        response.label_set.parent_id = echoed_1
        return response


async def handle_score_label_set(
    deps: Dependencies,
    request: labeling_v1_label_set_validation_service_pb2.ScoreLabelSetRequest
) -> labeling_v1_label_set_validation_service_pb2.ScoreLabelSetResponse:
    """Scores a label set."""
    response = labeling_v1_label_set_validation_service_pb2.ScoreLabelSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScoreLabelSet', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ScoreLabelSet', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = labeling_v1_label_set_calculation_service_pb2.QuoteLabelSetResponse()
        response_1 = ledger_v1_ledger_account_validation_service_pb2.LintLedgerAccountsResponse()
        response_2 = featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityResponse()
        outgoing_0 = labeling_v1_label_set_calculation_service_pb2.QuoteLabelSetRequest(
            context=request.context,
            label_set=labeling_v1_labeling_pb2.LabelSet(
                children=[
                    labeling_v1_labeling_pb2.LabelSet(
                        children=[
                            labeling_v1_labeling_pb2.LabelSet(
                                location=common_v1_address_pb2.PostalAddress(region=request.label_set.location.region)
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.labeling_label_set_calculation.QuoteLabelSet(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = ledger_v1_ledger_account_validation_service_pb2.LintLedgerAccountsRequest(
            context=request.context,
            details=ledger_v1_ledger_account_validation_service_pb2.LintLedgerAccountsRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=response_0.label_set.manager.email)
            ),
            ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
                holder=ledger_v1_refs_pb2.PostingBatchRef(display_name=request.label_set.manager.display_name),
                limits=[ledger_v1_ledger_pb2.LedgerAccountLimit(name=request.label_set.name)]
            )
        )
        response_1 = cast(ledger_v1_ledger_account_validation_service_pb2.LintLedgerAccountsResponse, await deps.bus.request(
            'acme.labeling.v1.LabelSetValidationService/ScoreLabelSet/1', outgoing_1, deps.settings.timeout,
        ))
        outgoing_2 = featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityRequest(
            context=request.context,
            details=featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=response_1.ledger_account.contact.email)
            ),
            feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.label_set.audit.created_at)
            )
        )
        response_2 = await deps.clients.featurestore_feature_view_validation.CheckFeatureViewEligibility(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.label_set.location.recipient
        if returned_0_0:
            response.label_set.location.recipient = returned_0_0
        returned_0_1 = response_0.label_set.label_set_id
        returned_0_1_part_1 = response.label_set.children.add()
        returned_0_1_part_2 = returned_0_1_part_1.children.add()
        returned_0_1_part_3 = returned_0_1_part_2.children.add()
        if returned_0_1:
            returned_0_1_part_3.label_set_id = returned_0_1
        returned_1_0 = response_1.ledger_account.holder.display_name
        if returned_1_0:
            response.label_set.manager.display_name = returned_1_0
        returned_2_0 = response_2.feature_view.address.recipient
        returned_2_0_part_1 = response.label_set.children.add()
        if returned_2_0:
            returned_2_0_part_1.location.recipient = returned_2_0
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.details.currency_code
        response.breakdown.currency_code = echoed_1
        return response


async def handle_validate_label_set(
    deps: Dependencies,
    request: labeling_v1_label_set_validation_service_pb2.ValidateLabelSetRequest
) -> labeling_v1_label_set_validation_service_pb2.ValidateLabelSetResponse:
    """Validates a label set."""
    response = labeling_v1_label_set_validation_service_pb2.ValidateLabelSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidateLabelSet', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidateLabelSet', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = labeling_v1_annotation_validation_service_pb2.CheckAnnotationEligibilityResponse()
        response_1 = metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesResponse()
        response_2 = lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionResponse()
        outgoing_0 = labeling_v1_annotation_validation_service_pb2.CheckAnnotationEligibilityRequest(
            annotation=labeling_v1_labeling_pb2.Annotation(
                subject=labeling_v1_refs_pb2.LabelingTaskRef(display_name=request.label_set.manager.display_name)
            ),
            context=request.context,
            details=labeling_v1_annotation_validation_service_pb2.CheckAnnotationEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.label_set.manager.email)
            )
        )
        response_0 = await deps.clients.labeling_annotation_validation.CheckAnnotationEligibility(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        fields_1: dict[str, Any] = {
            'context': request.context,
            'filter': {
                'created_after': request.label_set.audit.created_at,
                'labels': dict(request.label_set.attributes),
                'owner_id': response_0.annotation.correlation_id,
                'region': request.label_set.location.region
            }
        }
        outgoing_1 = metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesRequest(**fields_1)
        response_1 = await deps.clients.metrics_metric_series_query.BrowseMetricSerieses(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                comments=[lineage_v1_lineage_pb2.ImpactComment(created_at=request.label_set.audit.created_at)],
                customer=customers_v1_refs_pb2.CustomerRef(email=request.label_set.manager.email),
                requester=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
            )
        )
        document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
        outgoing_2 = ParseDict(document_2, lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionRequest())
        response_2 = await deps.clients.lineage_impact_validation.ExplainImpactDecision(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.result.message
        if returned_1_1:
            response.outcome.message = returned_1_1
        returned_2_0 = response_2.impact.assignee.display_name
        returned_2_0_part_1 = response.label_set.children.add()
        if returned_2_0:
            returned_2_0_part_1.manager.display_name = returned_2_0
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.label_set.parent_id
        response.label_set.parent_id = echoed_1
        return response
