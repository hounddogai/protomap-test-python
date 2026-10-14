"""Typed commands crossing the recommendations application boundary."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf import timestamp_pb2 as timestamp_pb2

from acme.admissions.v1 import admission_calculation_service_pb2 as admissions_v1_admission_calculation_service_pb2
from acme.admissions.v1 import admissions_pb2 as admissions_v1_admissions_pb2
from acme.admissions.v1 import refs_pb2 as admissions_v1_refs_pb2
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2 as anomalies_v1_anomaly_feedback_workflow_service_pb2,
)
from acme.campaigns.v1 import marketing_campaign_query_service_pb2 as campaigns_v1_marketing_campaign_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.concessions.v1 import concession_stand_query_service_pb2 as concessions_v1_concession_stand_query_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.media.v1 import media_asset_calculation_service_pb2 as media_v1_media_asset_calculation_service_pb2
from acme.media.v1 import media_pb2 as media_v1_media_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.notifications.v1 import refs_pb2 as notifications_v1_refs_pb2
from acme.pipelines.v1 import pipeline_run_sync_service_pb2 as pipelines_v1_pipeline_run_sync_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.recommendations.v1 import (
    interaction_calculation_service_pb2 as recommendations_v1_interaction_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2 as recommendations_v1_recommendation_set_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.platform.models import ValidatedModel


@dataclass(frozen=True, slots=True)
class InteractionCalculationExplainInteractionCalculation1Command:
    """Inputs required to validate recommendation set."""
    context: common_v1_context_pb2.RequestContext
    details_contact_email: str


def to_interaction_calculation_explain_interaction_calculation1_command(
    command: InteractionCalculationExplainInteractionCalculation1Command
) -> recommendations_v1_recommendation_set_validation_service_pb2.ValidateRecommendationSetRequest:
    return recommendations_v1_recommendation_set_validation_service_pb2.ValidateRecommendationSetRequest(
        context=command.context,
        details=recommendations_v1_recommendation_set_validation_service_pb2.ValidateRecommendationSetRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(email=command.details_contact_email)
        )
    )


@dataclass(frozen=True, slots=True)
class InteractionLifecycleActivateInteraction3Command:
    """Inputs required to resolve pipeline run conflict."""
    context: common_v1_context_pb2.RequestContext
    pipeline_run_assignee_email: str


def to_interaction_lifecycle_activate_interaction3_command(
    command: InteractionLifecycleActivateInteraction3Command
) -> pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictRequest:
    return pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictRequest(
        context=command.context,
        pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
            assignee=identity_v1_refs_pb2.UserRef(email=command.pipeline_run_assignee_email)
        )
    )


@dataclass(frozen=True, slots=True)
class InteractionLifecycleTerminateInteraction2Command:
    """Inputs required to explain media asset calculation."""
    context: common_v1_context_pb2.RequestContext
    media_asset_owner_email: str
    details_contact_email: str


def to_interaction_lifecycle_terminate_interaction2_command(
    command: InteractionLifecycleTerminateInteraction2Command
) -> media_v1_media_asset_calculation_service_pb2.ExplainMediaAssetCalculationRequest:
    return media_v1_media_asset_calculation_service_pb2.ExplainMediaAssetCalculationRequest(
        context=command.context,
        details=media_v1_media_asset_calculation_service_pb2.ExplainMediaAssetCalculationRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(email=command.details_contact_email)
        ),
        media_asset=media_v1_media_pb2.MediaAsset(
            owner=identity_v1_refs_pb2.UserRef(email=command.media_asset_owner_email)
        )
    )


@dataclass(frozen=True, slots=True)
class InteractionValidationCheckInteractionEligibility0Command(ValidatedModel):
    """Inputs required to summarize concession stands."""
    context: common_v1_context_pb2.RequestContext
    annotations: dict[str, str]


def to_interaction_validation_check_interaction_eligibility0_command(
    command: InteractionValidationCheckInteractionEligibility0Command
) -> concessions_v1_concession_stand_query_service_pb2.SummarizeConcessionStandsRequest:
    return concessions_v1_concession_stand_query_service_pb2.SummarizeConcessionStandsRequest(
        annotations=command.annotations,
        context=command.context
    )


@dataclass(frozen=True, slots=True)
class InteractionWorkflowListInteractionWorkflows1Command(ValidatedModel):
    """Inputs required to resolve marketing campaigns."""
    context: common_v1_context_pb2.RequestContext


def to_interaction_workflow_list_interaction_workflows1_command(
    command: InteractionWorkflowListInteractionWorkflows1Command
) -> campaigns_v1_marketing_campaign_query_service_pb2.ResolveMarketingCampaignsRequest:
    return campaigns_v1_marketing_campaign_query_service_pb2.ResolveMarketingCampaignsRequest(context=command.context)


@dataclass(frozen=True, slots=True)
class RecommendationModelApprovalCommentRecommendationModelApproval3Command:
    """Inputs required to quote recommendation model."""
    context: common_v1_context_pb2.RequestContext
    recommendation_model_owner_display_name: str


def to_recommendation_model_approval_comment_recommendation_model_approval3_command(
    command: RecommendationModelApprovalCommentRecommendationModelApproval3Command
) -> recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelRequest:
    return recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelRequest(
        context=command.context,
        recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
            owner=identity_v1_refs_pb2.UserRef(display_name=command.recommendation_model_owner_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class RecommendationModelCalculationCalculateRecommendationModel2Command:
    """Inputs required to compare annotation options."""
    context: common_v1_context_pb2.RequestContext
    details_destination_country_code: str
    details_destination_postal_code: str
    details_destination_lines: list[str]
    details_destination_locality: str


def to_recommendation_model_calculation_calculate_recommendation_model2_command(
    command: RecommendationModelCalculationCalculateRecommendationModel2Command
) -> labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest:
    return labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest(
        context=command.context,
        details=labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(
                country_code=command.details_destination_country_code,
                lines=command.details_destination_lines,
                locality=command.details_destination_locality,
                postal_code=command.details_destination_postal_code
            )
        )
    )


@dataclass(frozen=True, slots=True)
class RecommendationModelQueryExportRecommendationModels1Command:
    """Inputs required to calculate interaction."""
    context: common_v1_context_pb2.RequestContext
    interaction_subject_display_name: str
    interaction_correlation_id: str
    details_destination_region: str
    interaction_subject_email: str


def to_recommendation_model_query_export_recommendation_models1_command(
    command: RecommendationModelQueryExportRecommendationModels1Command
) -> recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionRequest:
    return recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionRequest(
        context=command.context,
        details=recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(region=command.details_destination_region)
        ),
        interaction=recommendations_v1_recommendations_pb2.Interaction(
            correlation_id=command.interaction_correlation_id,
            subject=customers_v1_refs_pb2.CustomerRef(
                display_name=command.interaction_subject_display_name,
                email=command.interaction_subject_email
            )
        )
    )


@dataclass(frozen=True, slots=True)
class RecommendationModelValidationPreviewRecommendationModel1Command:
    """Inputs required to check notification eligibility."""
    context: common_v1_context_pb2.RequestContext
    notification_assignee_user_id: str
    notification_audit_updated_at: timestamp_pb2.Timestamp
    notification_customer_display_name: str


def to_recommendation_model_validation_preview_recommendation_model1_command(
    command: RecommendationModelValidationPreviewRecommendationModel1Command
) -> notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityRequest:
    return notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityRequest(
        context=command.context,
        notification=notifications_v1_notifications_pb2.Notification(
            assignee=identity_v1_refs_pb2.UserRef(user_id=command.notification_assignee_user_id),
            audit=common_v1_audit_pb2.AuditInfo(updated_at=command.notification_audit_updated_at),
            customer=notifications_v1_refs_pb2.NotificationTemplateRef(
                display_name=command.notification_customer_display_name
            )
        )
    )


@dataclass(frozen=True, slots=True)
class RecommendationModelValidationScoreRecommendationModel0Command(ValidatedModel):
    """Inputs required to explain admission calculation."""
    context: common_v1_context_pb2.RequestContext
    details_contact_email: str
    admission_subject_display_name: str
    admission_measurements_unit: str
    reason: str


def to_recommendation_model_validation_score_recommendation_model0_command(
    command: RecommendationModelValidationScoreRecommendationModel0Command
) -> admissions_v1_admission_calculation_service_pb2.ExplainAdmissionCalculationRequest:
    return admissions_v1_admission_calculation_service_pb2.ExplainAdmissionCalculationRequest(
        admission=admissions_v1_admissions_pb2.Admission(
            measurements=[admissions_v1_admissions_pb2.AdmissionMeasurement(unit=command.admission_measurements_unit)],
            subject=admissions_v1_refs_pb2.GateScanRef(display_name=command.admission_subject_display_name)
        ),
        context=command.context,
        details=admissions_v1_admission_calculation_service_pb2.ExplainAdmissionCalculationRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(email=command.details_contact_email)
        ),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class RecommendationModelWorkflowResumeRecommendationModelWorkflow1Command:
    """Inputs required to retry anomaly feedback workflow."""
    context: common_v1_context_pb2.RequestContext
    details_notify_email: str
    anomaly_feedback_subject_code: str
    anomaly_feedback_subject_display_name: str


def to_recommendation_model_workflow_resume_recommendation_model_workflow1_command(
    command: RecommendationModelWorkflowResumeRecommendationModelWorkflow1Command
) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowRequest:
    return anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowRequest(
        anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
            subject=datasets_v1_refs_pb2.DatasetRef(
                code=command.anomaly_feedback_subject_code,
                display_name=command.anomaly_feedback_subject_display_name
            )
        ),
        context=command.context,
        details=anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowRequest.Details(
            notify=common_v1_contact_pb2.ContactInfo(email=command.details_notify_email)
        )
    )


@dataclass(frozen=True, slots=True)
class RecommendationModelWorkflowRetryRecommendationModelWorkflow0Command(ValidatedModel):
    """Inputs required to validate interaction."""
    context: common_v1_context_pb2.RequestContext
    interaction_subject_display_name: str
    details_contact_email: str
    interaction_measurements_unit: str
    details_contact_phone: str


def to_recommendation_model_workflow_retry_recommendation_model_workflow0_command(
    command: RecommendationModelWorkflowRetryRecommendationModelWorkflow0Command
) -> recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest:
    return recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest(
        context=command.context,
        details=recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(
                email=command.details_contact_email,
                phone=command.details_contact_phone
            )
        ),
        interaction=recommendations_v1_recommendations_pb2.Interaction(
            measurements=[
                recommendations_v1_recommendations_pb2.InteractionMeasurement(
                    unit=command.interaction_measurements_unit
                )
            ],
            subject=customers_v1_refs_pb2.CustomerRef(display_name=command.interaction_subject_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class RecommendationSetApprovalEscalateRecommendationSet0Command:
    """Inputs required to validate recommendation model."""
    context: common_v1_context_pb2.RequestContext
    recommendation_model_owner_email: str
    recommendation_model_audit_created_at: timestamp_pb2.Timestamp


def to_recommendation_set_approval_escalate_recommendation_set0_command(
    command: RecommendationSetApprovalEscalateRecommendationSet0Command
) -> recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelRequest:
    return recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelRequest(
        context=command.context,
        recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
            audit=common_v1_audit_pb2.AuditInfo(created_at=command.recommendation_model_audit_created_at),
            owner=identity_v1_refs_pb2.UserRef(email=command.recommendation_model_owner_email)
        )
    )


@dataclass(frozen=True, slots=True)
class RecommendationSetCreateRecommendationSet1Command(ValidatedModel):
    """Inputs required to browse venues."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp


def to_recommendation_set_create_recommendation_set1_command(
    command: RecommendationSetCreateRecommendationSet1Command
) -> venues_v1_venue_query_service_pb2.BrowseVenuesRequest:
    return venues_v1_venue_query_service_pb2.BrowseVenuesRequest(
        context=command.context,
        filter=venues_v1_venue_query_service_pb2.BrowseVenuesRequest.Filter(
            created_after=command.filter_created_after,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class RecommendationSetWorkflowResumeRecommendationSetWorkflow0Command(ValidatedModel):
    """Inputs required to explain recommendation model decision."""
    context: common_v1_context_pb2.RequestContext
    details_contact_email: str


def to_recommendation_set_workflow_resume_recommendation_set_workflow0_command(
    command: RecommendationSetWorkflowResumeRecommendationSetWorkflow0Command
) -> recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest:
    return recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest(
        context=command.context,
        details=recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(email=command.details_contact_email)
        )
    )
