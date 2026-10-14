"""Background event handlers owned by the datasets team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.compliance.v1 import (
    compliance_case_calculation_service_pb2 as compliance_v1_compliance_case_calculation_service_pb2,
)
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import dataset_version_workflow_service_pb2 as datasets_v1_dataset_version_workflow_service_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.seating.v1 import seat_map_service_pb2 as seating_v1_seat_map_service_pb2

from acme_data.domains.datasets.dependencies import Dependencies


async def on_data_schema_approval_service_delegate_data_schema_approval_3(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest, payload)
    return await deps.clients.datasets_dataset_validation.CheckDatasetEligibility(
        request,
        timeout=deps.settings.timeout
    )


async def on_data_schema_calculation_service_calculate_data_schema_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(seating_v1_seat_map_service_pb2.BatchGetSeatMapsRequest, payload)
    return await deps.clients.seating_seat_map.BatchGetSeatMaps(request, timeout=deps.settings.timeout)


async def on_data_schema_validation_service_check_data_schema_eligibility_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(datasets_v1_dataset_validation_service_pb2.ScoreDatasetRequest, payload)
    return await deps.clients.datasets_dataset_validation.ScoreDataset(request, timeout=deps.settings.timeout)


async def on_data_schema_workflow_service_advance_data_schema_workflow_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(datasets_v1_dataset_version_workflow_service_pb2.RetryDatasetVersionWorkflowRequest, payload)
    return await deps.clients.datasets_dataset_version_workflow.RetryDatasetVersionWorkflow(
        request,
        timeout=deps.settings.timeout
    )


async def on_dataset_approval_service_comment_dataset_approval_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(compliance_v1_compliance_case_calculation_service_pb2.RecalculateComplianceCasesRequest, payload)
    return await deps.clients.compliance_compliance_case_calculation.RecalculateComplianceCases(
        request,
        timeout=deps.settings.timeout
    )


async def on_dataset_service_delete_dataset_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityRequest, payload)
    return await deps.clients.datasets_data_schema_validation.CheckDataSchemaEligibility(
        request,
        timeout=deps.settings.timeout
    )


async def on_dataset_version_approval_service_delegate_dataset_version_approval_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(customers_v1_household_validation_service_pb2.ValidateHouseholdRequest, payload)
    return await deps.clients.customers_household_validation.ValidateHousehold(request, timeout=deps.settings.timeout)


async def on_dataset_version_calculation_service_estimate_dataset_version_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(notifications_v1_notification_query_service_pb2.ResolveNotificationsRequest, payload)
    return await deps.clients.notifications_notification_query.ResolveNotifications(
        request,
        timeout=deps.settings.timeout
    )


async def on_dataset_version_validation_service_preview_dataset_version_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest, payload)
    return await deps.clients.datasets_dataset_version_calculation.ExplainDatasetVersionCalculation(
        request,
        timeout=deps.settings.timeout
    )


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.datasets.v1.DataSchemaApprovalService/DelegateDataSchemaApproval/3',
        partial(on_data_schema_approval_service_delegate_data_schema_approval_3, deps)
    )
    deps.bus.subscribe(
        'acme.datasets.v1.DataSchemaCalculationService/CalculateDataSchema/0',
        partial(on_data_schema_calculation_service_calculate_data_schema_0, deps)
    )
    deps.bus.subscribe(
        'acme.datasets.v1.DataSchemaValidationService/CheckDataSchemaEligibility/1',
        partial(on_data_schema_validation_service_check_data_schema_eligibility_1, deps)
    )
    deps.bus.subscribe(
        'acme.datasets.v1.DataSchemaWorkflowService/AdvanceDataSchemaWorkflow/0',
        partial(on_data_schema_workflow_service_advance_data_schema_workflow_0, deps)
    )
    deps.bus.subscribe(
        'acme.datasets.v1.DatasetApprovalService/CommentDatasetApproval/0',
        partial(on_dataset_approval_service_comment_dataset_approval_0, deps)
    )
    deps.bus.subscribe(
        'acme.datasets.v1.DatasetService/DeleteDataset/0',
        partial(on_dataset_service_delete_dataset_0, deps)
    )
    deps.bus.subscribe(
        'acme.datasets.v1.DatasetVersionApprovalService/DelegateDatasetVersionApproval/0',
        partial(on_dataset_version_approval_service_delegate_dataset_version_approval_0, deps)
    )
    deps.bus.subscribe(
        'acme.datasets.v1.DatasetVersionCalculationService/EstimateDatasetVersion/0',
        partial(on_dataset_version_calculation_service_estimate_dataset_version_0, deps)
    )
    deps.bus.subscribe(
        'acme.datasets.v1.DatasetVersionValidationService/PreviewDatasetVersion/2',
        partial(on_dataset_version_validation_service_preview_dataset_version_2, deps)
    )
