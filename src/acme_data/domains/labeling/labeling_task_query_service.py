"""Answers read-only questions about labeling tasks, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2_grpc as labeling_v1_labeling_task_query_service_pb2_grpc

from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.labeling_task_query_service_operations import handle_browse_labeling_tasks
from acme_data.domains.labeling.labeling_task_query_service_operations import handle_count_labeling_tasks
from acme_data.domains.labeling.labeling_task_query_service_operations import handle_export_labeling_tasks
from acme_data.domains.labeling.labeling_task_query_service_operations import handle_find_labeling_tasks
from acme_data.domains.labeling.labeling_task_query_service_operations import handle_lookup_labeling_task
from acme_data.domains.labeling.labeling_task_query_service_operations import handle_peek_labeling_task
from acme_data.domains.labeling.labeling_task_query_service_operations import handle_resolve_labeling_tasks
from acme_data.domains.labeling.labeling_task_query_service_operations import handle_suggest_labeling_tasks
from acme_data.domains.labeling.labeling_task_query_service_operations import handle_summarize_labeling_tasks
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LabelingTaskQueryServicer(labeling_v1_labeling_task_query_service_pb2_grpc.LabelingTaskQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseLabelingTasks(
        self, request: labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksResponse:
        """Lists labeling tasks a page at a time."""
        return await handle_browse_labeling_tasks(self.deps, request)

    @rpc_errors
    @retry_transient
    async def CountLabelingTasks(
        self, request: labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksResponse:
        """Counts labeling tasks by status."""
        return await handle_count_labeling_tasks(self.deps, request)

    @stream_errors
    async def ExportLabelingTasks(
        self, request: labeling_v1_labeling_task_query_service_pb2.ExportLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[labeling_v1_labeling_task_query_service_pb2.ExportLabelingTasksResponse]:
        """Streams every matching labeling task."""
        response = await handle_export_labeling_tasks(self.deps, request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindLabelingTasks(
        self, request: labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksResponse:
        """Lists labeling tasks a page at a time."""
        return await handle_find_labeling_tasks(self.deps, request)

    @rpc_errors
    @retry_transient
    async def LookupLabelingTask(
        self, request: labeling_v1_labeling_task_query_service_pb2.LookupLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_query_service_pb2.LookupLabelingTaskResponse:
        """Returns a labeling task."""
        return await handle_lookup_labeling_task(self.deps, request)

    @rpc_errors
    @retry_transient
    async def PeekLabelingTask(
        self, request: labeling_v1_labeling_task_query_service_pb2.PeekLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_query_service_pb2.PeekLabelingTaskResponse:
        """Returns a labeling task."""
        return await handle_peek_labeling_task(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ResolveLabelingTasks(
        self, request: labeling_v1_labeling_task_query_service_pb2.ResolveLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_query_service_pb2.ResolveLabelingTasksResponse:
        """Returns several labeling tasks at once."""
        return await handle_resolve_labeling_tasks(self.deps, request)

    @rpc_errors
    @retry_transient
    async def SuggestLabelingTasks(
        self, request: labeling_v1_labeling_task_query_service_pb2.SuggestLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_query_service_pb2.SuggestLabelingTasksResponse:
        """Lists labeling tasks a page at a time."""
        return await handle_suggest_labeling_tasks(self.deps, request)

    @rpc_errors
    async def SummarizeLabelingTasks(
        self, request: labeling_v1_labeling_task_query_service_pb2.SummarizeLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_query_service_pb2.SummarizeLabelingTasksResponse:
        """Summarizes a labeling task."""
        return await handle_summarize_labeling_tasks(self.deps, request)
