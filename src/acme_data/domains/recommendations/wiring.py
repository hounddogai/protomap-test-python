"""Register and compose every service of the recommendations domain."""

from __future__ import annotations

import grpc

from acme.admissions.v1 import (
    admission_calculation_service_pb2_grpc as admissions_v1_admission_calculation_service_pb2_grpc,
)
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2_grpc as anomalies_v1_anomaly_feedback_approval_service_pb2_grpc,
)
from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2_grpc as anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_service_pb2_grpc as anomalies_v1_anomaly_service_pb2_grpc
from acme.anomalies.v1 import detector_validation_service_pb2_grpc as anomalies_v1_detector_validation_service_pb2_grpc
from acme.appointments.v1 import (
    appointment_query_service_pb2_grpc as appointments_v1_appointment_query_service_pb2_grpc,
)
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.audit.v1 import audit_event_service_pb2_grpc as audit_v1_audit_event_service_pb2_grpc
from acme.audit.v1 import audit_event_validation_service_pb2_grpc as audit_v1_audit_event_validation_service_pb2_grpc
from acme.authorization.v1 import access_policy_service_pb2_grpc as authorization_v1_access_policy_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.campaigns.v1 import (
    marketing_campaign_query_service_pb2_grpc as campaigns_v1_marketing_campaign_query_service_pb2_grpc,
)
from acme.concessions.v1 import (
    concession_stand_query_service_pb2_grpc as concessions_v1_concession_stand_query_service_pb2_grpc,
)
from acme.configuration.v1 import config_set_service_pb2_grpc as configuration_v1_config_set_service_pb2_grpc
from acme.contracts.v1 import contract_service_pb2_grpc as contracts_v1_contract_service_pb2_grpc
from acme.corporateevents.v1 import (
    corporate_event_service_pb2_grpc as corporateevents_v1_corporate_event_service_pb2_grpc,
)
from acme.customers.v1 import (
    consent_record_calculation_service_pb2_grpc as customers_v1_consent_record_calculation_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_calculation_service_pb2_grpc as customers_v1_customer_calculation_service_pb2_grpc,
)
from acme.customers.v1 import customer_query_service_pb2_grpc as customers_v1_customer_query_service_pb2_grpc
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2_grpc as customers_v1_customer_segment_calculation_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_segment_validation_service_pb2_grpc as customers_v1_customer_segment_validation_service_pb2_grpc,
)
from acme.customers.v1 import customer_service_pb2_grpc as customers_v1_customer_service_pb2_grpc
from acme.customers.v1 import customer_validation_service_pb2_grpc as customers_v1_customer_validation_service_pb2_grpc
from acme.customers.v1 import (
    household_calculation_service_pb2_grpc as customers_v1_household_calculation_service_pb2_grpc,
)
from acme.customers.v1 import household_query_service_pb2_grpc as customers_v1_household_query_service_pb2_grpc
from acme.customers.v1 import (
    household_validation_service_pb2_grpc as customers_v1_household_validation_service_pb2_grpc,
)
from acme.customers.v1 import (
    preference_calculation_service_pb2_grpc as customers_v1_preference_calculation_service_pb2_grpc,
)
from acme.customers.v1 import (
    preference_validation_service_pb2_grpc as customers_v1_preference_validation_service_pb2_grpc,
)
from acme.datasets.v1 import (
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import dataset_service_pb2_grpc as datasets_v1_dataset_service_pb2_grpc
from acme.datasets.v1 import dataset_validation_service_pb2_grpc as datasets_v1_dataset_validation_service_pb2_grpc
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2_grpc as datasets_v1_dataset_version_validation_service_pb2_grpc,
)
from acme.documents.v1 import document_validation_service_pb2_grpc as documents_v1_document_validation_service_pb2_grpc
from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_reporting_service_pb2_grpc as featurestore_v1_entity_reporting_service_pb2_grpc
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2_grpc as featurestore_v1_feature_value_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_query_service_pb2_grpc as featurestore_v1_feature_value_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2_grpc as featurestore_v1_feature_value_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_workflow_service_pb2_grpc as featurestore_v1_feature_value_workflow_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_view_service_pb2_grpc as featurestore_v1_feature_view_service_pb2_grpc
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_workflow_service_pb2_grpc as featurestore_v1_feature_view_workflow_service_pb2_grpc,
)
from acme.forms.v1 import form_service_pb2_grpc as forms_v1_form_service_pb2_grpc
from acme.fuel.v1 import fuel_card_query_service_pb2_grpc as fuel_v1_fuel_card_query_service_pb2_grpc
from acme.fuel.v1 import fuel_card_service_pb2_grpc as fuel_v1_fuel_card_service_pb2_grpc
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.keymanagement.v1 import crypto_key_service_pb2_grpc as keymanagement_v1_crypto_key_service_pb2_grpc
from acme.labeling.v1 import (
    annotation_calculation_service_pb2_grpc as labeling_v1_annotation_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_lifecycle_service_pb2_grpc as labeling_v1_label_set_lifecycle_service_pb2_grpc
from acme.labeling.v1 import label_set_workflow_service_pb2_grpc as labeling_v1_label_set_workflow_service_pb2_grpc
from acme.labeling.v1 import (
    labeling_task_approval_service_pb2_grpc as labeling_v1_labeling_task_approval_service_pb2_grpc,
)
from acme.labeling.v1 import labeling_task_query_service_pb2_grpc as labeling_v1_labeling_task_query_service_pb2_grpc
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.ledger.v1 import (
    ledger_account_validation_service_pb2_grpc as ledger_v1_ledger_account_validation_service_pb2_grpc,
)
from acme.lineage.v1 import impact_sync_service_pb2_grpc as lineage_v1_impact_sync_service_pb2_grpc
from acme.lineage.v1 import impact_validation_service_pb2_grpc as lineage_v1_impact_validation_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_query_service_pb2_grpc as lineage_v1_lineage_edge_query_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_edge_validation_service_pb2_grpc as lineage_v1_lineage_edge_validation_service_pb2_grpc,
)
from acme.lineage.v1 import (
    lineage_node_reporting_service_pb2_grpc as lineage_v1_lineage_node_reporting_service_pb2_grpc,
)
from acme.lineage.v1 import (
    lineage_node_validation_service_pb2_grpc as lineage_v1_lineage_node_validation_service_pb2_grpc,
)
from acme.maintenance.v1 import work_order_query_service_pb2_grpc as maintenance_v1_work_order_query_service_pb2_grpc
from acme.media.v1 import media_asset_calculation_service_pb2_grpc as media_v1_media_asset_calculation_service_pb2_grpc
from acme.metrics.v1 import dashboard_export_service_pb2_grpc as metrics_v1_dashboard_export_service_pb2_grpc
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
from acme.metrics.v1 import (
    dashboard_notification_service_pb2_grpc as metrics_v1_dashboard_notification_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_alert_export_service_pb2_grpc as metrics_v1_metric_alert_export_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_notification_service_pb2_grpc as metrics_v1_metric_alert_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_alert_query_service_pb2_grpc as metrics_v1_metric_alert_query_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_validation_service_pb2_grpc as metrics_v1_metric_alert_validation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_notification_service_pb2_grpc as metrics_v1_metric_series_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc
from acme.metrics.v1 import metric_series_service_pb2_grpc as metrics_v1_metric_series_service_pb2_grpc
from acme.modelregistry.v1 import (
    deployment_import_service_pb2_grpc as modelregistry_v1_deployment_import_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_workflow_service_pb2_grpc as modelregistry_v1_deployment_workflow_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2_grpc as modelregistry_v1_model_version_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2_grpc as modelregistry_v1_registered_model_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2_grpc as modelregistry_v1_registered_model_reporting_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_service_pb2_grpc as modelregistry_v1_registered_model_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2_grpc as modelregistry_v1_registered_model_validation_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_query_service_pb2_grpc as notifications_v1_notification_query_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_validation_service_pb2_grpc as notifications_v1_notification_validation_service_pb2_grpc,
)
from acme.patients.v1 import patient_query_service_pb2_grpc as patients_v1_patient_query_service_pb2_grpc
from acme.performers.v1 import performer_service_pb2_grpc as performers_v1_performer_service_pb2_grpc
from acme.pipelines.v1 import pipeline_approval_service_pb2_grpc as pipelines_v1_pipeline_approval_service_pb2_grpc
from acme.pipelines.v1 import pipeline_lifecycle_service_pb2_grpc as pipelines_v1_pipeline_lifecycle_service_pb2_grpc
from acme.pipelines.v1 import pipeline_run_sync_service_pb2_grpc as pipelines_v1_pipeline_run_sync_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_step_export_service_pb2_grpc as pipelines_v1_pipeline_step_export_service_pb2_grpc,
)
from acme.pricing.v1 import price_list_service_pb2_grpc as pricing_v1_price_list_service_pb2_grpc
from acme.ratelimiting.v1 import (
    rate_limit_calculation_service_pb2_grpc as ratelimiting_v1_rate_limit_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    interaction_approval_service_pb2_grpc as recommendations_v1_interaction_approval_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    interaction_calculation_service_pb2_grpc as recommendations_v1_interaction_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    interaction_lifecycle_service_pb2_grpc as recommendations_v1_interaction_lifecycle_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    interaction_validation_service_pb2_grpc as recommendations_v1_interaction_validation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    interaction_workflow_service_pb2_grpc as recommendations_v1_interaction_workflow_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_approval_service_pb2_grpc as recommendations_v1_recommendation_model_approval_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2_grpc as recommendations_v1_recommendation_model_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_query_service_pb2_grpc as recommendations_v1_recommendation_model_query_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2_grpc as recommendations_v1_recommendation_model_validation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2_grpc as recommendations_v1_recommendation_model_workflow_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_approval_service_pb2_grpc as recommendations_v1_recommendation_set_approval_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2_grpc as recommendations_v1_recommendation_set_query_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_service_pb2_grpc as recommendations_v1_recommendation_set_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2_grpc as recommendations_v1_recommendation_set_validation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_workflow_service_pb2_grpc as recommendations_v1_recommendation_set_workflow_service_pb2_grpc,
)
from acme.search.v1 import search_index_query_service_pb2_grpc as search_v1_search_index_query_service_pb2_grpc
from acme.shows.v1 import show_calculation_service_pb2_grpc as shows_v1_show_calculation_service_pb2_grpc
from acme.sponsorships.v1 import sponsor_query_service_pb2_grpc as sponsorships_v1_sponsor_query_service_pb2_grpc
from acme.telehealth.v1 import video_visit_query_service_pb2_grpc as telehealth_v1_video_visit_query_service_pb2_grpc
from acme.telematics.v1 import (
    telemetry_reading_calculation_service_pb2_grpc as telematics_v1_telemetry_reading_calculation_service_pb2_grpc,
)
from acme.venues.v1 import venue_query_service_pb2_grpc as venues_v1_venue_query_service_pb2_grpc
from acme.venues.v1 import venue_service_pb2_grpc as venues_v1_venue_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc
from acme.yards.v1 import yard_query_service_pb2_grpc as yards_v1_yard_query_service_pb2_grpc

from acme_data.domains.recommendations.dependencies import Clients
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.events import subscribe
from acme_data.domains.recommendations.interaction_approval_service import InteractionApprovalServicer
from acme_data.domains.recommendations.interaction_calculation_service import InteractionCalculationServicer
from acme_data.domains.recommendations.interaction_lifecycle_service import InteractionLifecycleServicer
from acme_data.domains.recommendations.interaction_validation_service import InteractionValidationServicer
from acme_data.domains.recommendations.interaction_workflow_service import InteractionWorkflowServicer
from acme_data.domains.recommendations.recommendation_model_approval_service import RecommendationModelApprovalServicer
from acme_data.domains.recommendations.recommendation_model_calculation_service import (
    RecommendationModelCalculationServicer,
)
from acme_data.domains.recommendations.recommendation_model_query_service import RecommendationModelQueryServicer
from acme_data.domains.recommendations.recommendation_model_validation_service import (
    RecommendationModelValidationServicer,
)
from acme_data.domains.recommendations.recommendation_model_workflow_service import RecommendationModelWorkflowServicer
from acme_data.domains.recommendations.recommendation_set_approval_service import RecommendationSetApprovalServicer
from acme_data.domains.recommendations.recommendation_set_query_service import RecommendationSetQueryServicer
from acme_data.domains.recommendations.recommendation_set_service import RecommendationSetServicer
from acme_data.domains.recommendations.recommendation_set_validation_service import RecommendationSetValidationServicer
from acme_data.domains.recommendations.recommendation_set_workflow_service import RecommendationSetWorkflowServicer
from acme_data.domains.recommendations.repository import DomainRepository
from acme_data.platform.container import Container
from acme_data.platform.container import Factory


def dependencies(container: Container) -> Dependencies:
    admissions_admission_calculation = container.singleton(
        admissions_v1_admission_calculation_service_pb2_grpc.AdmissionCalculationServiceStub,
        lambda: admissions_v1_admission_calculation_service_pb2_grpc.AdmissionCalculationServiceStub(container.channel)
    )
    anomalies_anomaly_feedback_approval = container.singleton(
        anomalies_v1_anomaly_feedback_approval_service_pb2_grpc.AnomalyFeedbackApprovalServiceStub,
        lambda: anomalies_v1_anomaly_feedback_approval_service_pb2_grpc.AnomalyFeedbackApprovalServiceStub(
            container.channel
        )
    )
    anomalies_anomaly_feedback_workflow = container.singleton(
        anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc.AnomalyFeedbackWorkflowServiceStub,
        lambda: anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc.AnomalyFeedbackWorkflowServiceStub(
            container.channel
        )
    )
    anomalies_anomaly = container.singleton(
        anomalies_v1_anomaly_service_pb2_grpc.AnomalyServiceStub,
        lambda: anomalies_v1_anomaly_service_pb2_grpc.AnomalyServiceStub(container.channel)
    )
    anomalies_detector_validation = container.singleton(
        anomalies_v1_detector_validation_service_pb2_grpc.DetectorValidationServiceStub,
        lambda: anomalies_v1_detector_validation_service_pb2_grpc.DetectorValidationServiceStub(container.channel)
    )
    appointments_appointment_query = container.singleton(
        appointments_v1_appointment_query_service_pb2_grpc.AppointmentQueryServiceStub,
        lambda: appointments_v1_appointment_query_service_pb2_grpc.AppointmentQueryServiceStub(container.channel)
    )
    audit_audit_event_query = container.singleton(
        audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub,
        lambda: audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub(container.channel)
    )
    audit_audit_event = container.singleton(
        audit_v1_audit_event_service_pb2_grpc.AuditEventServiceStub,
        lambda: audit_v1_audit_event_service_pb2_grpc.AuditEventServiceStub(container.channel)
    )
    audit_audit_event_validation = container.singleton(
        audit_v1_audit_event_validation_service_pb2_grpc.AuditEventValidationServiceStub,
        lambda: audit_v1_audit_event_validation_service_pb2_grpc.AuditEventValidationServiceStub(container.channel)
    )
    authorization_access_policy = container.singleton(
        authorization_v1_access_policy_service_pb2_grpc.AccessPolicyServiceStub,
        lambda: authorization_v1_access_policy_service_pb2_grpc.AccessPolicyServiceStub(container.channel)
    )
    authorization_access_policy_validation = container.singleton(
        authorization_v1_access_policy_validation_service_pb2_grpc.AccessPolicyValidationServiceStub,
        lambda: authorization_v1_access_policy_validation_service_pb2_grpc.AccessPolicyValidationServiceStub(
            container.channel
        )
    )
    campaigns_marketing_campaign_query = container.singleton(
        campaigns_v1_marketing_campaign_query_service_pb2_grpc.MarketingCampaignQueryServiceStub,
        lambda: campaigns_v1_marketing_campaign_query_service_pb2_grpc.MarketingCampaignQueryServiceStub(
            container.channel
        )
    )
    concessions_concession_stand_query = container.singleton(
        concessions_v1_concession_stand_query_service_pb2_grpc.ConcessionStandQueryServiceStub,
        lambda: concessions_v1_concession_stand_query_service_pb2_grpc.ConcessionStandQueryServiceStub(
            container.channel
        )
    )
    configuration_config_set = container.singleton(
        configuration_v1_config_set_service_pb2_grpc.ConfigSetServiceStub,
        lambda: configuration_v1_config_set_service_pb2_grpc.ConfigSetServiceStub(container.channel)
    )
    contracts_contract = container.singleton(
        contracts_v1_contract_service_pb2_grpc.ContractServiceStub,
        lambda: contracts_v1_contract_service_pb2_grpc.ContractServiceStub(container.channel)
    )
    corporateevents_corporate_event = container.singleton(
        corporateevents_v1_corporate_event_service_pb2_grpc.CorporateEventServiceStub,
        lambda: corporateevents_v1_corporate_event_service_pb2_grpc.CorporateEventServiceStub(container.channel)
    )
    customers_consent_record_calculation = container.singleton(
        customers_v1_consent_record_calculation_service_pb2_grpc.ConsentRecordCalculationServiceStub,
        lambda: customers_v1_consent_record_calculation_service_pb2_grpc.ConsentRecordCalculationServiceStub(
            container.channel
        )
    )
    customers_customer_calculation = container.singleton(
        customers_v1_customer_calculation_service_pb2_grpc.CustomerCalculationServiceStub,
        lambda: customers_v1_customer_calculation_service_pb2_grpc.CustomerCalculationServiceStub(container.channel)
    )
    customers_customer_query = container.singleton(
        customers_v1_customer_query_service_pb2_grpc.CustomerQueryServiceStub,
        lambda: customers_v1_customer_query_service_pb2_grpc.CustomerQueryServiceStub(container.channel)
    )
    customers_customer_segment_calculation = container.singleton(
        customers_v1_customer_segment_calculation_service_pb2_grpc.CustomerSegmentCalculationServiceStub,
        lambda: customers_v1_customer_segment_calculation_service_pb2_grpc.CustomerSegmentCalculationServiceStub(
            container.channel
        )
    )
    customers_customer_segment_validation = container.singleton(
        customers_v1_customer_segment_validation_service_pb2_grpc.CustomerSegmentValidationServiceStub,
        lambda: customers_v1_customer_segment_validation_service_pb2_grpc.CustomerSegmentValidationServiceStub(
            container.channel
        )
    )
    customers_customer = container.singleton(
        customers_v1_customer_service_pb2_grpc.CustomerServiceStub,
        lambda: customers_v1_customer_service_pb2_grpc.CustomerServiceStub(container.channel)
    )
    customers_customer_validation = container.singleton(
        customers_v1_customer_validation_service_pb2_grpc.CustomerValidationServiceStub,
        lambda: customers_v1_customer_validation_service_pb2_grpc.CustomerValidationServiceStub(container.channel)
    )
    customers_household_calculation = container.singleton(
        customers_v1_household_calculation_service_pb2_grpc.HouseholdCalculationServiceStub,
        lambda: customers_v1_household_calculation_service_pb2_grpc.HouseholdCalculationServiceStub(container.channel)
    )
    customers_household_query = container.singleton(
        customers_v1_household_query_service_pb2_grpc.HouseholdQueryServiceStub,
        lambda: customers_v1_household_query_service_pb2_grpc.HouseholdQueryServiceStub(container.channel)
    )
    customers_household_validation = container.singleton(
        customers_v1_household_validation_service_pb2_grpc.HouseholdValidationServiceStub,
        lambda: customers_v1_household_validation_service_pb2_grpc.HouseholdValidationServiceStub(container.channel)
    )
    customers_preference_calculation = container.singleton(
        customers_v1_preference_calculation_service_pb2_grpc.PreferenceCalculationServiceStub,
        lambda: customers_v1_preference_calculation_service_pb2_grpc.PreferenceCalculationServiceStub(container.channel)
    )
    customers_preference_validation = container.singleton(
        customers_v1_preference_validation_service_pb2_grpc.PreferenceValidationServiceStub,
        lambda: customers_v1_preference_validation_service_pb2_grpc.PreferenceValidationServiceStub(container.channel)
    )
    datasets_data_schema_calculation = container.singleton(
        datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
        lambda: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub(container.channel)
    )
    datasets_dataset = container.singleton(
        datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub,
        lambda: datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub(container.channel)
    )
    datasets_dataset_validation = container.singleton(
        datasets_v1_dataset_validation_service_pb2_grpc.DatasetValidationServiceStub,
        lambda: datasets_v1_dataset_validation_service_pb2_grpc.DatasetValidationServiceStub(container.channel)
    )
    datasets_dataset_version_validation = container.singleton(
        datasets_v1_dataset_version_validation_service_pb2_grpc.DatasetVersionValidationServiceStub,
        lambda: datasets_v1_dataset_version_validation_service_pb2_grpc.DatasetVersionValidationServiceStub(
            container.channel
        )
    )
    documents_document_validation = container.singleton(
        documents_v1_document_validation_service_pb2_grpc.DocumentValidationServiceStub,
        lambda: documents_v1_document_validation_service_pb2_grpc.DocumentValidationServiceStub(container.channel)
    )
    featureflags_feature_flag = container.singleton(
        featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub,
        lambda: featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub(container.channel)
    )
    featureflags_feature_flag_validation = container.singleton(
        featureflags_v1_feature_flag_validation_service_pb2_grpc.FeatureFlagValidationServiceStub,
        lambda: featureflags_v1_feature_flag_validation_service_pb2_grpc.FeatureFlagValidationServiceStub(
            container.channel
        )
    )
    featurestore_entity_reporting = container.singleton(
        featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceStub,
        lambda: featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceStub(container.channel)
    )
    featurestore_feature_value_calculation = container.singleton(
        featurestore_v1_feature_value_calculation_service_pb2_grpc.FeatureValueCalculationServiceStub,
        lambda: featurestore_v1_feature_value_calculation_service_pb2_grpc.FeatureValueCalculationServiceStub(
            container.channel
        )
    )
    featurestore_feature_value_query = container.singleton(
        featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceStub,
        lambda: featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceStub(container.channel)
    )
    featurestore_feature_value_validation = container.singleton(
        featurestore_v1_feature_value_validation_service_pb2_grpc.FeatureValueValidationServiceStub,
        lambda: featurestore_v1_feature_value_validation_service_pb2_grpc.FeatureValueValidationServiceStub(
            container.channel
        )
    )
    featurestore_feature_value_workflow = container.singleton(
        featurestore_v1_feature_value_workflow_service_pb2_grpc.FeatureValueWorkflowServiceStub,
        lambda: featurestore_v1_feature_value_workflow_service_pb2_grpc.FeatureValueWorkflowServiceStub(
            container.channel
        )
    )
    featurestore_feature_view_calculation = container.singleton(
        featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceStub,
        lambda: featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceStub(
            container.channel
        )
    )
    featurestore_feature_view = container.singleton(
        featurestore_v1_feature_view_service_pb2_grpc.FeatureViewServiceStub,
        lambda: featurestore_v1_feature_view_service_pb2_grpc.FeatureViewServiceStub(container.channel)
    )
    featurestore_feature_view_validation = container.singleton(
        featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub,
        lambda: featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub(
            container.channel
        )
    )
    featurestore_feature_view_workflow = container.singleton(
        featurestore_v1_feature_view_workflow_service_pb2_grpc.FeatureViewWorkflowServiceStub,
        lambda: featurestore_v1_feature_view_workflow_service_pb2_grpc.FeatureViewWorkflowServiceStub(container.channel)
    )
    forms_form = container.singleton(
        forms_v1_form_service_pb2_grpc.FormServiceStub,
        lambda: forms_v1_form_service_pb2_grpc.FormServiceStub(container.channel)
    )
    fuel_fuel_card_query = container.singleton(
        fuel_v1_fuel_card_query_service_pb2_grpc.FuelCardQueryServiceStub,
        lambda: fuel_v1_fuel_card_query_service_pb2_grpc.FuelCardQueryServiceStub(container.channel)
    )
    fuel_fuel_card = container.singleton(
        fuel_v1_fuel_card_service_pb2_grpc.FuelCardServiceStub,
        lambda: fuel_v1_fuel_card_service_pb2_grpc.FuelCardServiceStub(container.channel)
    )
    identity_user_query = container.singleton(
        identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
        lambda: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub(container.channel)
    )
    identity_user_validation = container.singleton(
        identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
        lambda: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub(container.channel)
    )
    keymanagement_crypto_key = container.singleton(
        keymanagement_v1_crypto_key_service_pb2_grpc.CryptoKeyServiceStub,
        lambda: keymanagement_v1_crypto_key_service_pb2_grpc.CryptoKeyServiceStub(container.channel)
    )
    labeling_annotation_calculation = container.singleton(
        labeling_v1_annotation_calculation_service_pb2_grpc.AnnotationCalculationServiceStub,
        lambda: labeling_v1_annotation_calculation_service_pb2_grpc.AnnotationCalculationServiceStub(container.channel)
    )
    labeling_label_set_lifecycle = container.singleton(
        labeling_v1_label_set_lifecycle_service_pb2_grpc.LabelSetLifecycleServiceStub,
        lambda: labeling_v1_label_set_lifecycle_service_pb2_grpc.LabelSetLifecycleServiceStub(container.channel)
    )
    labeling_label_set_workflow = container.singleton(
        labeling_v1_label_set_workflow_service_pb2_grpc.LabelSetWorkflowServiceStub,
        lambda: labeling_v1_label_set_workflow_service_pb2_grpc.LabelSetWorkflowServiceStub(container.channel)
    )
    labeling_labeling_task_approval = container.singleton(
        labeling_v1_labeling_task_approval_service_pb2_grpc.LabelingTaskApprovalServiceStub,
        lambda: labeling_v1_labeling_task_approval_service_pb2_grpc.LabelingTaskApprovalServiceStub(container.channel)
    )
    labeling_labeling_task_query = container.singleton(
        labeling_v1_labeling_task_query_service_pb2_grpc.LabelingTaskQueryServiceStub,
        lambda: labeling_v1_labeling_task_query_service_pb2_grpc.LabelingTaskQueryServiceStub(container.channel)
    )
    ledger_ledger_account_query = container.singleton(
        ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub,
        lambda: ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub(container.channel)
    )
    ledger_ledger_account = container.singleton(
        ledger_v1_ledger_account_service_pb2_grpc.LedgerAccountServiceStub,
        lambda: ledger_v1_ledger_account_service_pb2_grpc.LedgerAccountServiceStub(container.channel)
    )
    ledger_ledger_account_validation = container.singleton(
        ledger_v1_ledger_account_validation_service_pb2_grpc.LedgerAccountValidationServiceStub,
        lambda: ledger_v1_ledger_account_validation_service_pb2_grpc.LedgerAccountValidationServiceStub(
            container.channel
        )
    )
    lineage_impact_sync = container.singleton(
        lineage_v1_impact_sync_service_pb2_grpc.ImpactSyncServiceStub,
        lambda: lineage_v1_impact_sync_service_pb2_grpc.ImpactSyncServiceStub(container.channel)
    )
    lineage_impact_validation = container.singleton(
        lineage_v1_impact_validation_service_pb2_grpc.ImpactValidationServiceStub,
        lambda: lineage_v1_impact_validation_service_pb2_grpc.ImpactValidationServiceStub(container.channel)
    )
    lineage_lineage_edge_query = container.singleton(
        lineage_v1_lineage_edge_query_service_pb2_grpc.LineageEdgeQueryServiceStub,
        lambda: lineage_v1_lineage_edge_query_service_pb2_grpc.LineageEdgeQueryServiceStub(container.channel)
    )
    lineage_lineage_edge_validation = container.singleton(
        lineage_v1_lineage_edge_validation_service_pb2_grpc.LineageEdgeValidationServiceStub,
        lambda: lineage_v1_lineage_edge_validation_service_pb2_grpc.LineageEdgeValidationServiceStub(container.channel)
    )
    lineage_lineage_node_reporting = container.singleton(
        lineage_v1_lineage_node_reporting_service_pb2_grpc.LineageNodeReportingServiceStub,
        lambda: lineage_v1_lineage_node_reporting_service_pb2_grpc.LineageNodeReportingServiceStub(container.channel)
    )
    lineage_lineage_node_validation = container.singleton(
        lineage_v1_lineage_node_validation_service_pb2_grpc.LineageNodeValidationServiceStub,
        lambda: lineage_v1_lineage_node_validation_service_pb2_grpc.LineageNodeValidationServiceStub(container.channel)
    )
    maintenance_work_order_query = container.singleton(
        maintenance_v1_work_order_query_service_pb2_grpc.WorkOrderQueryServiceStub,
        lambda: maintenance_v1_work_order_query_service_pb2_grpc.WorkOrderQueryServiceStub(container.channel)
    )
    media_media_asset_calculation = container.singleton(
        media_v1_media_asset_calculation_service_pb2_grpc.MediaAssetCalculationServiceStub,
        lambda: media_v1_media_asset_calculation_service_pb2_grpc.MediaAssetCalculationServiceStub(container.channel)
    )
    metrics_dashboard_export = container.singleton(
        metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub,
        lambda: metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub(container.channel)
    )
    metrics_dashboard_history = container.singleton(
        metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub,
        lambda: metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub(container.channel)
    )
    metrics_dashboard_notification = container.singleton(
        metrics_v1_dashboard_notification_service_pb2_grpc.DashboardNotificationServiceStub,
        lambda: metrics_v1_dashboard_notification_service_pb2_grpc.DashboardNotificationServiceStub(container.channel)
    )
    metrics_dashboard_validation = container.singleton(
        metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub,
        lambda: metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub(container.channel)
    )
    metrics_metric_alert_export = container.singleton(
        metrics_v1_metric_alert_export_service_pb2_grpc.MetricAlertExportServiceStub,
        lambda: metrics_v1_metric_alert_export_service_pb2_grpc.MetricAlertExportServiceStub(container.channel)
    )
    metrics_metric_alert_notification = container.singleton(
        metrics_v1_metric_alert_notification_service_pb2_grpc.MetricAlertNotificationServiceStub,
        lambda: metrics_v1_metric_alert_notification_service_pb2_grpc.MetricAlertNotificationServiceStub(
            container.channel
        )
    )
    metrics_metric_alert_query = container.singleton(
        metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub,
        lambda: metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub(container.channel)
    )
    metrics_metric_alert_validation = container.singleton(
        metrics_v1_metric_alert_validation_service_pb2_grpc.MetricAlertValidationServiceStub,
        lambda: metrics_v1_metric_alert_validation_service_pb2_grpc.MetricAlertValidationServiceStub(container.channel)
    )
    metrics_metric_series_export = container.singleton(
        metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub,
        lambda: metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub(container.channel)
    )
    metrics_metric_series_history = container.singleton(
        metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub,
        lambda: metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub(container.channel)
    )
    metrics_metric_series_notification = container.singleton(
        metrics_v1_metric_series_notification_service_pb2_grpc.MetricSeriesNotificationServiceStub,
        lambda: metrics_v1_metric_series_notification_service_pb2_grpc.MetricSeriesNotificationServiceStub(
            container.channel
        )
    )
    metrics_metric_series_query = container.singleton(
        metrics_v1_metric_series_query_service_pb2_grpc.MetricSeriesQueryServiceStub,
        lambda: metrics_v1_metric_series_query_service_pb2_grpc.MetricSeriesQueryServiceStub(container.channel)
    )
    metrics_metric_series = container.singleton(
        metrics_v1_metric_series_service_pb2_grpc.MetricSeriesServiceStub,
        lambda: metrics_v1_metric_series_service_pb2_grpc.MetricSeriesServiceStub(container.channel)
    )
    modelregistry_deployment_import = container.singleton(
        modelregistry_v1_deployment_import_service_pb2_grpc.DeploymentImportServiceStub,
        lambda: modelregistry_v1_deployment_import_service_pb2_grpc.DeploymentImportServiceStub(container.channel)
    )
    modelregistry_deployment_workflow = container.singleton(
        modelregistry_v1_deployment_workflow_service_pb2_grpc.DeploymentWorkflowServiceStub,
        lambda: modelregistry_v1_deployment_workflow_service_pb2_grpc.DeploymentWorkflowServiceStub(container.channel)
    )
    modelregistry_model_version_validation = container.singleton(
        modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub,
        lambda: modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_calculation = container.singleton(
        modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub,
        lambda: modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_reporting = container.singleton(
        modelregistry_v1_registered_model_reporting_service_pb2_grpc.RegisteredModelReportingServiceStub,
        lambda: modelregistry_v1_registered_model_reporting_service_pb2_grpc.RegisteredModelReportingServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model = container.singleton(
        modelregistry_v1_registered_model_service_pb2_grpc.RegisteredModelServiceStub,
        lambda: modelregistry_v1_registered_model_service_pb2_grpc.RegisteredModelServiceStub(container.channel)
    )
    modelregistry_registered_model_validation = container.singleton(
        modelregistry_v1_registered_model_validation_service_pb2_grpc.RegisteredModelValidationServiceStub,
        lambda: modelregistry_v1_registered_model_validation_service_pb2_grpc.RegisteredModelValidationServiceStub(
            container.channel
        )
    )
    notifications_notification_query = container.singleton(
        notifications_v1_notification_query_service_pb2_grpc.NotificationQueryServiceStub,
        lambda: notifications_v1_notification_query_service_pb2_grpc.NotificationQueryServiceStub(container.channel)
    )
    notifications_notification_validation = container.singleton(
        notifications_v1_notification_validation_service_pb2_grpc.NotificationValidationServiceStub,
        lambda: notifications_v1_notification_validation_service_pb2_grpc.NotificationValidationServiceStub(
            container.channel
        )
    )
    patients_patient_query = container.singleton(
        patients_v1_patient_query_service_pb2_grpc.PatientQueryServiceStub,
        lambda: patients_v1_patient_query_service_pb2_grpc.PatientQueryServiceStub(container.channel)
    )
    performers_performer = container.singleton(
        performers_v1_performer_service_pb2_grpc.PerformerServiceStub,
        lambda: performers_v1_performer_service_pb2_grpc.PerformerServiceStub(container.channel)
    )
    pipelines_pipeline_approval = container.singleton(
        pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceStub,
        lambda: pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceStub(container.channel)
    )
    pipelines_pipeline_lifecycle = container.singleton(
        pipelines_v1_pipeline_lifecycle_service_pb2_grpc.PipelineLifecycleServiceStub,
        lambda: pipelines_v1_pipeline_lifecycle_service_pb2_grpc.PipelineLifecycleServiceStub(container.channel)
    )
    pipelines_pipeline_run_sync = container.singleton(
        pipelines_v1_pipeline_run_sync_service_pb2_grpc.PipelineRunSyncServiceStub,
        lambda: pipelines_v1_pipeline_run_sync_service_pb2_grpc.PipelineRunSyncServiceStub(container.channel)
    )
    pipelines_pipeline_step_export = container.singleton(
        pipelines_v1_pipeline_step_export_service_pb2_grpc.PipelineStepExportServiceStub,
        lambda: pipelines_v1_pipeline_step_export_service_pb2_grpc.PipelineStepExportServiceStub(container.channel)
    )
    pricing_price_list = container.singleton(
        pricing_v1_price_list_service_pb2_grpc.PriceListServiceStub,
        lambda: pricing_v1_price_list_service_pb2_grpc.PriceListServiceStub(container.channel)
    )
    ratelimiting_rate_limit_calculation = container.singleton(
        ratelimiting_v1_rate_limit_calculation_service_pb2_grpc.RateLimitCalculationServiceStub,
        lambda: ratelimiting_v1_rate_limit_calculation_service_pb2_grpc.RateLimitCalculationServiceStub(
            container.channel
        )
    )
    recommendations_interaction_calculation = container.singleton(
        recommendations_v1_interaction_calculation_service_pb2_grpc.InteractionCalculationServiceStub,
        lambda: recommendations_v1_interaction_calculation_service_pb2_grpc.InteractionCalculationServiceStub(
            container.channel
        )
    )
    recommendations_interaction_lifecycle = container.singleton(
        recommendations_v1_interaction_lifecycle_service_pb2_grpc.InteractionLifecycleServiceStub,
        lambda: recommendations_v1_interaction_lifecycle_service_pb2_grpc.InteractionLifecycleServiceStub(
            container.channel
        )
    )
    recommendations_interaction_validation = container.singleton(
        recommendations_v1_interaction_validation_service_pb2_grpc.InteractionValidationServiceStub,
        lambda: recommendations_v1_interaction_validation_service_pb2_grpc.InteractionValidationServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_model_approval = container.singleton(
        recommendations_v1_recommendation_model_approval_service_pb2_grpc.RecommendationModelApprovalServiceStub,
        lambda: recommendations_v1_recommendation_model_approval_service_pb2_grpc.RecommendationModelApprovalServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_model_calculation = container.singleton(
        recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub,
        lambda: recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_model_query = container.singleton(
        recommendations_v1_recommendation_model_query_service_pb2_grpc.RecommendationModelQueryServiceStub,
        lambda: recommendations_v1_recommendation_model_query_service_pb2_grpc.RecommendationModelQueryServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_model_validation = container.singleton(
        recommendations_v1_recommendation_model_validation_service_pb2_grpc.RecommendationModelValidationServiceStub,
        lambda: recommendations_v1_recommendation_model_validation_service_pb2_grpc.RecommendationModelValidationServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_model_workflow = container.singleton(
        recommendations_v1_recommendation_model_workflow_service_pb2_grpc.RecommendationModelWorkflowServiceStub,
        lambda: recommendations_v1_recommendation_model_workflow_service_pb2_grpc.RecommendationModelWorkflowServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_set_approval = container.singleton(
        recommendations_v1_recommendation_set_approval_service_pb2_grpc.RecommendationSetApprovalServiceStub,
        lambda: recommendations_v1_recommendation_set_approval_service_pb2_grpc.RecommendationSetApprovalServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_set_query = container.singleton(
        recommendations_v1_recommendation_set_query_service_pb2_grpc.RecommendationSetQueryServiceStub,
        lambda: recommendations_v1_recommendation_set_query_service_pb2_grpc.RecommendationSetQueryServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_set = container.singleton(
        recommendations_v1_recommendation_set_service_pb2_grpc.RecommendationSetServiceStub,
        lambda: recommendations_v1_recommendation_set_service_pb2_grpc.RecommendationSetServiceStub(container.channel)
    )
    recommendations_recommendation_set_validation = container.singleton(
        recommendations_v1_recommendation_set_validation_service_pb2_grpc.RecommendationSetValidationServiceStub,
        lambda: recommendations_v1_recommendation_set_validation_service_pb2_grpc.RecommendationSetValidationServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_set_workflow = container.singleton(
        recommendations_v1_recommendation_set_workflow_service_pb2_grpc.RecommendationSetWorkflowServiceStub,
        lambda: recommendations_v1_recommendation_set_workflow_service_pb2_grpc.RecommendationSetWorkflowServiceStub(
            container.channel
        )
    )
    search_search_index_query = container.singleton(
        search_v1_search_index_query_service_pb2_grpc.SearchIndexQueryServiceStub,
        lambda: search_v1_search_index_query_service_pb2_grpc.SearchIndexQueryServiceStub(container.channel)
    )
    shows_show_calculation = container.singleton(
        shows_v1_show_calculation_service_pb2_grpc.ShowCalculationServiceStub,
        lambda: shows_v1_show_calculation_service_pb2_grpc.ShowCalculationServiceStub(container.channel)
    )
    sponsorships_sponsor_query = container.singleton(
        sponsorships_v1_sponsor_query_service_pb2_grpc.SponsorQueryServiceStub,
        lambda: sponsorships_v1_sponsor_query_service_pb2_grpc.SponsorQueryServiceStub(container.channel)
    )
    telehealth_video_visit_query = container.singleton(
        telehealth_v1_video_visit_query_service_pb2_grpc.VideoVisitQueryServiceStub,
        lambda: telehealth_v1_video_visit_query_service_pb2_grpc.VideoVisitQueryServiceStub(container.channel)
    )
    telematics_telemetry_reading_calculation = container.singleton(
        telematics_v1_telemetry_reading_calculation_service_pb2_grpc.TelemetryReadingCalculationServiceStub,
        lambda: telematics_v1_telemetry_reading_calculation_service_pb2_grpc.TelemetryReadingCalculationServiceStub(
            container.channel
        )
    )
    venues_venue_query = container.singleton(
        venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub,
        lambda: venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub(container.channel)
    )
    venues_venue = container.singleton(
        venues_v1_venue_service_pb2_grpc.VenueServiceStub,
        lambda: venues_v1_venue_service_pb2_grpc.VenueServiceStub(container.channel)
    )
    venues_venue_validation = container.singleton(
        venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
        lambda: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub(container.channel)
    )
    yards_yard_query = container.singleton(
        yards_v1_yard_query_service_pb2_grpc.YardQueryServiceStub,
        lambda: yards_v1_yard_query_service_pb2_grpc.YardQueryServiceStub(container.channel)
    )
    clients = Clients(
        admissions_admission_calculation=admissions_admission_calculation,
        anomalies_anomaly_feedback_approval=anomalies_anomaly_feedback_approval,
        anomalies_anomaly_feedback_workflow=anomalies_anomaly_feedback_workflow,
        anomalies_anomaly=anomalies_anomaly,
        anomalies_detector_validation=anomalies_detector_validation,
        appointments_appointment_query=appointments_appointment_query,
        audit_audit_event_query=audit_audit_event_query,
        audit_audit_event=audit_audit_event,
        audit_audit_event_validation=audit_audit_event_validation,
        authorization_access_policy=authorization_access_policy,
        authorization_access_policy_validation=authorization_access_policy_validation,
        campaigns_marketing_campaign_query=campaigns_marketing_campaign_query,
        concessions_concession_stand_query=concessions_concession_stand_query,
        configuration_config_set=configuration_config_set,
        contracts_contract=contracts_contract,
        corporateevents_corporate_event=corporateevents_corporate_event,
        customers_consent_record_calculation=customers_consent_record_calculation,
        customers_customer_calculation=customers_customer_calculation,
        customers_customer_query=customers_customer_query,
        customers_customer_segment_calculation=customers_customer_segment_calculation,
        customers_customer_segment_validation=customers_customer_segment_validation,
        customers_customer=customers_customer,
        customers_customer_validation=customers_customer_validation,
        customers_household_calculation=customers_household_calculation,
        customers_household_query=customers_household_query,
        customers_household_validation=customers_household_validation,
        customers_preference_calculation=customers_preference_calculation,
        customers_preference_validation=customers_preference_validation,
        datasets_data_schema_calculation=datasets_data_schema_calculation,
        datasets_dataset=datasets_dataset,
        datasets_dataset_validation=datasets_dataset_validation,
        datasets_dataset_version_validation=datasets_dataset_version_validation,
        documents_document_validation=documents_document_validation,
        featureflags_feature_flag=featureflags_feature_flag,
        featureflags_feature_flag_validation=featureflags_feature_flag_validation,
        featurestore_entity_reporting=featurestore_entity_reporting,
        featurestore_feature_value_calculation=featurestore_feature_value_calculation,
        featurestore_feature_value_query=featurestore_feature_value_query,
        featurestore_feature_value_validation=featurestore_feature_value_validation,
        featurestore_feature_value_workflow=featurestore_feature_value_workflow,
        featurestore_feature_view_calculation=featurestore_feature_view_calculation,
        featurestore_feature_view=featurestore_feature_view,
        featurestore_feature_view_validation=featurestore_feature_view_validation,
        featurestore_feature_view_workflow=featurestore_feature_view_workflow,
        forms_form=forms_form,
        fuel_fuel_card_query=fuel_fuel_card_query,
        fuel_fuel_card=fuel_fuel_card,
        identity_user_query=identity_user_query,
        identity_user_validation=identity_user_validation,
        keymanagement_crypto_key=keymanagement_crypto_key,
        labeling_annotation_calculation=labeling_annotation_calculation,
        labeling_label_set_lifecycle=labeling_label_set_lifecycle,
        labeling_label_set_workflow=labeling_label_set_workflow,
        labeling_labeling_task_approval=labeling_labeling_task_approval,
        labeling_labeling_task_query=labeling_labeling_task_query,
        ledger_ledger_account_query=ledger_ledger_account_query,
        ledger_ledger_account=ledger_ledger_account,
        ledger_ledger_account_validation=ledger_ledger_account_validation,
        lineage_impact_sync=lineage_impact_sync,
        lineage_impact_validation=lineage_impact_validation,
        lineage_lineage_edge_query=lineage_lineage_edge_query,
        lineage_lineage_edge_validation=lineage_lineage_edge_validation,
        lineage_lineage_node_reporting=lineage_lineage_node_reporting,
        lineage_lineage_node_validation=lineage_lineage_node_validation,
        maintenance_work_order_query=maintenance_work_order_query,
        media_media_asset_calculation=media_media_asset_calculation,
        metrics_dashboard_export=metrics_dashboard_export,
        metrics_dashboard_history=metrics_dashboard_history,
        metrics_dashboard_notification=metrics_dashboard_notification,
        metrics_dashboard_validation=metrics_dashboard_validation,
        metrics_metric_alert_export=metrics_metric_alert_export,
        metrics_metric_alert_notification=metrics_metric_alert_notification,
        metrics_metric_alert_query=metrics_metric_alert_query,
        metrics_metric_alert_validation=metrics_metric_alert_validation,
        metrics_metric_series_export=metrics_metric_series_export,
        metrics_metric_series_history=metrics_metric_series_history,
        metrics_metric_series_notification=metrics_metric_series_notification,
        metrics_metric_series_query=metrics_metric_series_query,
        metrics_metric_series=metrics_metric_series,
        modelregistry_deployment_import=modelregistry_deployment_import,
        modelregistry_deployment_workflow=modelregistry_deployment_workflow,
        modelregistry_model_version_validation=modelregistry_model_version_validation,
        modelregistry_registered_model_calculation=modelregistry_registered_model_calculation,
        modelregistry_registered_model_reporting=modelregistry_registered_model_reporting,
        modelregistry_registered_model=modelregistry_registered_model,
        modelregistry_registered_model_validation=modelregistry_registered_model_validation,
        notifications_notification_query=notifications_notification_query,
        notifications_notification_validation=notifications_notification_validation,
        patients_patient_query=patients_patient_query,
        performers_performer=performers_performer,
        pipelines_pipeline_approval=pipelines_pipeline_approval,
        pipelines_pipeline_lifecycle=pipelines_pipeline_lifecycle,
        pipelines_pipeline_run_sync=pipelines_pipeline_run_sync,
        pipelines_pipeline_step_export=pipelines_pipeline_step_export,
        pricing_price_list=pricing_price_list,
        ratelimiting_rate_limit_calculation=ratelimiting_rate_limit_calculation,
        recommendations_interaction_calculation=recommendations_interaction_calculation,
        recommendations_interaction_lifecycle=recommendations_interaction_lifecycle,
        recommendations_interaction_validation=recommendations_interaction_validation,
        recommendations_recommendation_model_approval=recommendations_recommendation_model_approval,
        recommendations_recommendation_model_calculation=recommendations_recommendation_model_calculation,
        recommendations_recommendation_model_query=recommendations_recommendation_model_query,
        recommendations_recommendation_model_validation=recommendations_recommendation_model_validation,
        recommendations_recommendation_model_workflow=recommendations_recommendation_model_workflow,
        recommendations_recommendation_set_approval=recommendations_recommendation_set_approval,
        recommendations_recommendation_set_query=recommendations_recommendation_set_query,
        recommendations_recommendation_set=recommendations_recommendation_set,
        recommendations_recommendation_set_validation=recommendations_recommendation_set_validation,
        recommendations_recommendation_set_workflow=recommendations_recommendation_set_workflow,
        search_search_index_query=search_search_index_query,
        shows_show_calculation=shows_show_calculation,
        sponsorships_sponsor_query=sponsorships_sponsor_query,
        telehealth_video_visit_query=telehealth_video_visit_query,
        telematics_telemetry_reading_calculation=telematics_telemetry_reading_calculation,
        venues_venue_query=venues_venue_query,
        venues_venue=venues_venue,
        venues_venue_validation=venues_venue_validation,
        yards_yard_query=yards_yard_query,
        registry={
            'acme.admissions.v1.AdmissionCalculationService': admissions_admission_calculation,
            'acme.anomalies.v1.AnomalyFeedbackApprovalService': anomalies_anomaly_feedback_approval,
            'acme.anomalies.v1.AnomalyFeedbackWorkflowService': anomalies_anomaly_feedback_workflow,
            'acme.anomalies.v1.AnomalyService': anomalies_anomaly,
            'acme.anomalies.v1.DetectorValidationService': anomalies_detector_validation,
            'acme.appointments.v1.AppointmentQueryService': appointments_appointment_query,
            'acme.audit.v1.AuditEventQueryService': audit_audit_event_query,
            'acme.audit.v1.AuditEventService': audit_audit_event,
            'acme.audit.v1.AuditEventValidationService': audit_audit_event_validation,
            'acme.authorization.v1.AccessPolicyService': authorization_access_policy,
            'acme.authorization.v1.AccessPolicyValidationService': authorization_access_policy_validation,
            'acme.campaigns.v1.MarketingCampaignQueryService': campaigns_marketing_campaign_query,
            'acme.concessions.v1.ConcessionStandQueryService': concessions_concession_stand_query,
            'acme.configuration.v1.ConfigSetService': configuration_config_set,
            'acme.contracts.v1.ContractService': contracts_contract,
            'acme.corporateevents.v1.CorporateEventService': corporateevents_corporate_event,
            'acme.customers.v1.ConsentRecordCalculationService': customers_consent_record_calculation,
            'acme.customers.v1.CustomerCalculationService': customers_customer_calculation,
            'acme.customers.v1.CustomerQueryService': customers_customer_query,
            'acme.customers.v1.CustomerSegmentCalculationService': customers_customer_segment_calculation,
            'acme.customers.v1.CustomerSegmentValidationService': customers_customer_segment_validation,
            'acme.customers.v1.CustomerService': customers_customer,
            'acme.customers.v1.CustomerValidationService': customers_customer_validation,
            'acme.customers.v1.HouseholdCalculationService': customers_household_calculation,
            'acme.customers.v1.HouseholdQueryService': customers_household_query,
            'acme.customers.v1.HouseholdValidationService': customers_household_validation,
            'acme.customers.v1.PreferenceCalculationService': customers_preference_calculation,
            'acme.customers.v1.PreferenceValidationService': customers_preference_validation,
            'acme.datasets.v1.DataSchemaCalculationService': datasets_data_schema_calculation,
            'acme.datasets.v1.DatasetService': datasets_dataset,
            'acme.datasets.v1.DatasetValidationService': datasets_dataset_validation,
            'acme.datasets.v1.DatasetVersionValidationService': datasets_dataset_version_validation,
            'acme.documents.v1.DocumentValidationService': documents_document_validation,
            'acme.featureflags.v1.FeatureFlagService': featureflags_feature_flag,
            'acme.featureflags.v1.FeatureFlagValidationService': featureflags_feature_flag_validation,
            'acme.featurestore.v1.EntityReportingService': featurestore_entity_reporting,
            'acme.featurestore.v1.FeatureValueCalculationService': featurestore_feature_value_calculation,
            'acme.featurestore.v1.FeatureValueQueryService': featurestore_feature_value_query,
            'acme.featurestore.v1.FeatureValueValidationService': featurestore_feature_value_validation,
            'acme.featurestore.v1.FeatureValueWorkflowService': featurestore_feature_value_workflow,
            'acme.featurestore.v1.FeatureViewCalculationService': featurestore_feature_view_calculation,
            'acme.featurestore.v1.FeatureViewService': featurestore_feature_view,
            'acme.featurestore.v1.FeatureViewValidationService': featurestore_feature_view_validation,
            'acme.featurestore.v1.FeatureViewWorkflowService': featurestore_feature_view_workflow,
            'acme.forms.v1.FormService': forms_form,
            'acme.fuel.v1.FuelCardQueryService': fuel_fuel_card_query,
            'acme.fuel.v1.FuelCardService': fuel_fuel_card,
            'acme.identity.v1.UserQueryService': identity_user_query,
            'acme.identity.v1.UserValidationService': identity_user_validation,
            'acme.keymanagement.v1.CryptoKeyService': keymanagement_crypto_key,
            'acme.labeling.v1.AnnotationCalculationService': labeling_annotation_calculation,
            'acme.labeling.v1.LabelSetLifecycleService': labeling_label_set_lifecycle,
            'acme.labeling.v1.LabelSetWorkflowService': labeling_label_set_workflow,
            'acme.labeling.v1.LabelingTaskApprovalService': labeling_labeling_task_approval,
            'acme.labeling.v1.LabelingTaskQueryService': labeling_labeling_task_query,
            'acme.ledger.v1.LedgerAccountQueryService': ledger_ledger_account_query,
            'acme.ledger.v1.LedgerAccountService': ledger_ledger_account,
            'acme.ledger.v1.LedgerAccountValidationService': ledger_ledger_account_validation,
            'acme.lineage.v1.ImpactSyncService': lineage_impact_sync,
            'acme.lineage.v1.ImpactValidationService': lineage_impact_validation,
            'acme.lineage.v1.LineageEdgeQueryService': lineage_lineage_edge_query,
            'acme.lineage.v1.LineageEdgeValidationService': lineage_lineage_edge_validation,
            'acme.lineage.v1.LineageNodeReportingService': lineage_lineage_node_reporting,
            'acme.lineage.v1.LineageNodeValidationService': lineage_lineage_node_validation,
            'acme.maintenance.v1.WorkOrderQueryService': maintenance_work_order_query,
            'acme.media.v1.MediaAssetCalculationService': media_media_asset_calculation,
            'acme.metrics.v1.DashboardExportService': metrics_dashboard_export,
            'acme.metrics.v1.DashboardHistoryService': metrics_dashboard_history,
            'acme.metrics.v1.DashboardNotificationService': metrics_dashboard_notification,
            'acme.metrics.v1.DashboardValidationService': metrics_dashboard_validation,
            'acme.metrics.v1.MetricAlertExportService': metrics_metric_alert_export,
            'acme.metrics.v1.MetricAlertNotificationService': metrics_metric_alert_notification,
            'acme.metrics.v1.MetricAlertQueryService': metrics_metric_alert_query,
            'acme.metrics.v1.MetricAlertValidationService': metrics_metric_alert_validation,
            'acme.metrics.v1.MetricSeriesExportService': metrics_metric_series_export,
            'acme.metrics.v1.MetricSeriesHistoryService': metrics_metric_series_history,
            'acme.metrics.v1.MetricSeriesNotificationService': metrics_metric_series_notification,
            'acme.metrics.v1.MetricSeriesQueryService': metrics_metric_series_query,
            'acme.metrics.v1.MetricSeriesService': metrics_metric_series,
            'acme.modelregistry.v1.DeploymentImportService': modelregistry_deployment_import,
            'acme.modelregistry.v1.DeploymentWorkflowService': modelregistry_deployment_workflow,
            'acme.modelregistry.v1.ModelVersionValidationService': modelregistry_model_version_validation,
            'acme.modelregistry.v1.RegisteredModelCalculationService': modelregistry_registered_model_calculation,
            'acme.modelregistry.v1.RegisteredModelReportingService': modelregistry_registered_model_reporting,
            'acme.modelregistry.v1.RegisteredModelService': modelregistry_registered_model,
            'acme.modelregistry.v1.RegisteredModelValidationService': modelregistry_registered_model_validation,
            'acme.notifications.v1.NotificationQueryService': notifications_notification_query,
            'acme.notifications.v1.NotificationValidationService': notifications_notification_validation,
            'acme.patients.v1.PatientQueryService': patients_patient_query,
            'acme.performers.v1.PerformerService': performers_performer,
            'acme.pipelines.v1.PipelineApprovalService': pipelines_pipeline_approval,
            'acme.pipelines.v1.PipelineLifecycleService': pipelines_pipeline_lifecycle,
            'acme.pipelines.v1.PipelineRunSyncService': pipelines_pipeline_run_sync,
            'acme.pipelines.v1.PipelineStepExportService': pipelines_pipeline_step_export,
            'acme.pricing.v1.PriceListService': pricing_price_list,
            'acme.ratelimiting.v1.RateLimitCalculationService': ratelimiting_rate_limit_calculation,
            'acme.recommendations.v1.InteractionCalculationService': recommendations_interaction_calculation,
            'acme.recommendations.v1.InteractionLifecycleService': recommendations_interaction_lifecycle,
            'acme.recommendations.v1.InteractionValidationService': recommendations_interaction_validation,
            'acme.recommendations.v1.RecommendationModelApprovalService': recommendations_recommendation_model_approval,
            'acme.recommendations.v1.RecommendationModelCalculationService': recommendations_recommendation_model_calculation,
            'acme.recommendations.v1.RecommendationModelQueryService': recommendations_recommendation_model_query,
            'acme.recommendations.v1.RecommendationModelValidationService': recommendations_recommendation_model_validation,
            'acme.recommendations.v1.RecommendationModelWorkflowService': recommendations_recommendation_model_workflow,
            'acme.recommendations.v1.RecommendationSetApprovalService': recommendations_recommendation_set_approval,
            'acme.recommendations.v1.RecommendationSetQueryService': recommendations_recommendation_set_query,
            'acme.recommendations.v1.RecommendationSetService': recommendations_recommendation_set,
            'acme.recommendations.v1.RecommendationSetValidationService': recommendations_recommendation_set_validation,
            'acme.recommendations.v1.RecommendationSetWorkflowService': recommendations_recommendation_set_workflow,
            'acme.search.v1.SearchIndexQueryService': search_search_index_query,
            'acme.shows.v1.ShowCalculationService': shows_show_calculation,
            'acme.sponsorships.v1.SponsorQueryService': sponsorships_sponsor_query,
            'acme.telehealth.v1.VideoVisitQueryService': telehealth_video_visit_query,
            'acme.telematics.v1.TelemetryReadingCalculationService': telematics_telemetry_reading_calculation,
            'acme.venues.v1.VenueQueryService': venues_venue_query,
            'acme.venues.v1.VenueService': venues_venue,
            'acme.venues.v1.VenueValidationService': venues_venue_validation,
            'acme.yards.v1.YardQueryService': yards_yard_query,
        },
    )
    return Dependencies(clients, DomainRepository(container.sessions),
                        container.settings, container.bus)


def register(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    deps = dependencies(container)
    registered: dict[str, object] = {}
    interaction_approval_servicer = Factory(lambda: InteractionApprovalServicer(deps))()
    recommendations_v1_interaction_approval_service_pb2_grpc.add_InteractionApprovalServiceServicer_to_server(
        interaction_approval_servicer,
        server
    )
    registered['acme.recommendations.v1.InteractionApprovalService'] = interaction_approval_servicer
    interaction_calculation_servicer = Factory(lambda: InteractionCalculationServicer(deps))()
    recommendations_v1_interaction_calculation_service_pb2_grpc.add_InteractionCalculationServiceServicer_to_server(
        interaction_calculation_servicer,
        server
    )
    registered['acme.recommendations.v1.InteractionCalculationService'] = interaction_calculation_servicer
    interaction_lifecycle_servicer = Factory(lambda: InteractionLifecycleServicer(deps))()
    recommendations_v1_interaction_lifecycle_service_pb2_grpc.add_InteractionLifecycleServiceServicer_to_server(
        interaction_lifecycle_servicer,
        server
    )
    registered['acme.recommendations.v1.InteractionLifecycleService'] = interaction_lifecycle_servicer
    interaction_validation_servicer = Factory(lambda: InteractionValidationServicer(deps))()
    recommendations_v1_interaction_validation_service_pb2_grpc.add_InteractionValidationServiceServicer_to_server(
        interaction_validation_servicer,
        server
    )
    registered['acme.recommendations.v1.InteractionValidationService'] = interaction_validation_servicer
    interaction_workflow_servicer = Factory(lambda: InteractionWorkflowServicer(deps))()
    recommendations_v1_interaction_workflow_service_pb2_grpc.add_InteractionWorkflowServiceServicer_to_server(
        interaction_workflow_servicer,
        server
    )
    registered['acme.recommendations.v1.InteractionWorkflowService'] = interaction_workflow_servicer
    recommendation_model_approval_servicer = Factory(lambda: RecommendationModelApprovalServicer(deps))()
    recommendations_v1_recommendation_model_approval_service_pb2_grpc.add_RecommendationModelApprovalServiceServicer_to_server(
        recommendation_model_approval_servicer,
        server
    )
    registered['acme.recommendations.v1.RecommendationModelApprovalService'] = recommendation_model_approval_servicer
    recommendation_model_calculation_servicer = Factory(lambda: RecommendationModelCalculationServicer(deps))()
    recommendations_v1_recommendation_model_calculation_service_pb2_grpc.add_RecommendationModelCalculationServiceServicer_to_server(
        recommendation_model_calculation_servicer,
        server
    )
    registered[
        'acme.recommendations.v1.RecommendationModelCalculationService'
    ] = recommendation_model_calculation_servicer
    recommendation_model_query_servicer = Factory(lambda: RecommendationModelQueryServicer(deps))()
    recommendations_v1_recommendation_model_query_service_pb2_grpc.add_RecommendationModelQueryServiceServicer_to_server(
        recommendation_model_query_servicer,
        server
    )
    registered['acme.recommendations.v1.RecommendationModelQueryService'] = recommendation_model_query_servicer
    recommendation_model_validation_servicer = Factory(lambda: RecommendationModelValidationServicer(deps))()
    recommendations_v1_recommendation_model_validation_service_pb2_grpc.add_RecommendationModelValidationServiceServicer_to_server(
        recommendation_model_validation_servicer,
        server
    )
    registered[
        'acme.recommendations.v1.RecommendationModelValidationService'
    ] = recommendation_model_validation_servicer
    recommendation_model_workflow_servicer = Factory(lambda: RecommendationModelWorkflowServicer(deps))()
    recommendations_v1_recommendation_model_workflow_service_pb2_grpc.add_RecommendationModelWorkflowServiceServicer_to_server(
        recommendation_model_workflow_servicer,
        server
    )
    registered['acme.recommendations.v1.RecommendationModelWorkflowService'] = recommendation_model_workflow_servicer
    recommendation_set_approval_servicer = Factory(lambda: RecommendationSetApprovalServicer(deps))()
    recommendations_v1_recommendation_set_approval_service_pb2_grpc.add_RecommendationSetApprovalServiceServicer_to_server(
        recommendation_set_approval_servicer,
        server
    )
    registered['acme.recommendations.v1.RecommendationSetApprovalService'] = recommendation_set_approval_servicer
    recommendation_set_query_servicer = Factory(lambda: RecommendationSetQueryServicer(deps))()
    recommendations_v1_recommendation_set_query_service_pb2_grpc.add_RecommendationSetQueryServiceServicer_to_server(
        recommendation_set_query_servicer,
        server
    )
    registered['acme.recommendations.v1.RecommendationSetQueryService'] = recommendation_set_query_servicer
    recommendation_set_servicer = Factory(lambda: RecommendationSetServicer(deps))()
    recommendations_v1_recommendation_set_service_pb2_grpc.add_RecommendationSetServiceServicer_to_server(
        recommendation_set_servicer,
        server
    )
    registered['acme.recommendations.v1.RecommendationSetService'] = recommendation_set_servicer
    recommendation_set_validation_servicer = Factory(lambda: RecommendationSetValidationServicer(deps))()
    recommendations_v1_recommendation_set_validation_service_pb2_grpc.add_RecommendationSetValidationServiceServicer_to_server(
        recommendation_set_validation_servicer,
        server
    )
    registered['acme.recommendations.v1.RecommendationSetValidationService'] = recommendation_set_validation_servicer
    recommendation_set_workflow_servicer = Factory(lambda: RecommendationSetWorkflowServicer(deps))()
    recommendations_v1_recommendation_set_workflow_service_pb2_grpc.add_RecommendationSetWorkflowServiceServicer_to_server(
        recommendation_set_workflow_servicer,
        server
    )
    registered['acme.recommendations.v1.RecommendationSetWorkflowService'] = recommendation_set_workflow_servicer
    subscribe(deps)
    return registered
