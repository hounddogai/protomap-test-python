"""Manages notebooks: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import notebook_service_pb2 as datahub_v1_notebook_service_pb2
from acme.datahub.v1 import notebook_service_pb2_grpc as datahub_v1_notebook_service_pb2_grpc

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.notebook_service_operations import handle_batch_create_notebooks
from acme_data.domains.datahub.notebook_service_operations import handle_clone_notebook
from acme_data.domains.datahub.notebook_service_operations import handle_create_notebook
from acme_data.domains.datahub.notebook_service_operations import handle_delete_notebook
from acme_data.domains.datahub.notebook_service_operations import handle_get_notebook
from acme_data.domains.datahub.notebook_service_operations import handle_list_notebooks
from acme_data.domains.datahub.notebook_service_operations import handle_update_notebook
from acme_data.domains.datahub.notebook_service_operations import handle_watch_notebooks
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class NotebookServicer(datahub_v1_notebook_service_pb2_grpc.NotebookServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def BatchCreateNotebooks(
        self, requests: AsyncIterator[
            datahub_v1_notebook_service_pb2.BatchCreateNotebooksRequest
        ], context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_service_pb2.BatchCreateNotebooksResponse:
        """Takes a stream of notebooks and answers once at the end."""
        response = datahub_v1_notebook_service_pb2.BatchCreateNotebooksResponse()
        async for request in requests:
            response.MergeFrom(await handle_batch_create_notebooks(self.deps, request))
        return response

    @rpc_errors
    async def CloneNotebook(
        self, request: datahub_v1_notebook_service_pb2.CloneNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_service_pb2.CloneNotebookResponse:
        """Creates a notebook."""
        return await handle_clone_notebook(self.deps, request)

    @rpc_errors
    async def CreateNotebook(
        self, request: datahub_v1_notebook_service_pb2.CreateNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_service_pb2.CreateNotebookResponse:
        """Creates a notebook."""
        return await handle_create_notebook(self.deps, request)

    @rpc_errors
    async def DeleteNotebook(
        self, request: datahub_v1_notebook_service_pb2.DeleteNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_service_pb2.DeleteNotebookResponse:
        """Deletes a notebook."""
        return await handle_delete_notebook(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetNotebook(
        self, request: datahub_v1_notebook_service_pb2.GetNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_service_pb2.GetNotebookResponse:
        """Returns a notebook."""
        return await handle_get_notebook(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListNotebooks(
        self, request: datahub_v1_notebook_service_pb2.ListNotebooksRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_service_pb2.ListNotebooksResponse:
        """Lists notebooks a page at a time."""
        return await handle_list_notebooks(self.deps, request)

    @rpc_errors
    async def UpdateNotebook(
        self, request: datahub_v1_notebook_service_pb2.UpdateNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_service_pb2.UpdateNotebookResponse:
        """Changes a notebook."""
        return await handle_update_notebook(self.deps, request)

    @stream_errors
    async def WatchNotebooks(
        self, request: datahub_v1_notebook_service_pb2.WatchNotebooksRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_notebook_service_pb2.WatchNotebooksResponse]:
        """Streams the changes of notebooks as they happen."""
        response = await handle_watch_notebooks(self.deps, request)
        for item in messages((response,)):
            yield item
