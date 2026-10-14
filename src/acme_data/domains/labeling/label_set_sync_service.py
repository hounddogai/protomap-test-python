"""Keeps label sets in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2_grpc as labeling_v1_label_set_sync_service_pb2_grpc

from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.label_set_sync_service_workflow import LabelSetSyncServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LabelSetSyncServicer(labeling_v1_label_set_sync_service_pb2_grpc.LabelSetSyncServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = LabelSetSyncServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def ListLabelSetConflicts(
        self, request: labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsResponse:
        """Lists label sets a page at a time."""
        return await self.workflow.handle_list_label_set_conflicts(request)

    @rpc_errors
    async def PullLabelSets(
        self, request: labeling_v1_label_set_sync_service_pb2.PullLabelSetsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_sync_service_pb2.PullLabelSetsResponse:
        """Pulls a label set."""
        return await self.workflow.handle_pull_label_sets(request)

    @rpc_errors
    async def PushLabelSet(
        self, request: labeling_v1_label_set_sync_service_pb2.PushLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_sync_service_pb2.PushLabelSetResponse:
        """Pushs a label set."""
        return await self.workflow.handle_push_label_set(request)

    @rpc_errors
    async def ResolveLabelSetConflict(
        self, request: labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictResponse:
        """Resolves a label set."""
        return await self.workflow.handle_resolve_label_set_conflict(request)

    @stream_errors
    async def StreamLabelSetChanges(
        self, requests: AsyncIterator[
            labeling_v1_label_set_sync_service_pb2.StreamLabelSetChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[labeling_v1_label_set_sync_service_pb2.StreamLabelSetChangesResponse]:
        """Exchanges changes of label sets with a peer."""
        async for request in requests:
            yield await self.workflow.handle_stream_label_set_changes(request)

    @rpc_errors
    async def SyncLabelSets(
        self, request: labeling_v1_label_set_sync_service_pb2.SyncLabelSetsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_sync_service_pb2.SyncLabelSetsResponse:
        """Syncs a label set."""
        return await self.workflow.handle_sync_label_sets(request)
