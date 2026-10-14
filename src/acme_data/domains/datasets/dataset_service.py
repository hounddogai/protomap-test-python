"""Manages datasets: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import dataset_service_pb2_grpc as datasets_v1_dataset_service_pb2_grpc

from acme_data.domains.datasets.dataset_service_workflow import DatasetServicerWorkflow
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DatasetServicer(datasets_v1_dataset_service_pb2_grpc.DatasetServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = DatasetServicerWorkflow(deps)

    @rpc_errors
    async def BatchCreateDatasets(
        self, requests: AsyncIterator[
            datasets_v1_dataset_service_pb2.BatchCreateDatasetsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_service_pb2.BatchCreateDatasetsResponse:
        """Takes a stream of datasets and answers once at the end."""
        response = datasets_v1_dataset_service_pb2.BatchCreateDatasetsResponse()
        async for request in requests:
            response.MergeFrom(await self.workflow.handle_batch_create_datasets(request))
        return response

    @rpc_errors
    @retry_transient
    async def BatchGetDatasets(
        self, request: datasets_v1_dataset_service_pb2.BatchGetDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_service_pb2.BatchGetDatasetsResponse:
        """Returns several datasets at once."""
        return await self.workflow.handle_batch_get_datasets(request)

    @rpc_errors
    async def CloneDataset(
        self, request: datasets_v1_dataset_service_pb2.CloneDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_service_pb2.CloneDatasetResponse:
        """Creates a dataset."""
        return await self.workflow.handle_clone_dataset(request)

    @rpc_errors
    async def CreateDataset(
        self, request: datasets_v1_dataset_service_pb2.CreateDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_service_pb2.CreateDatasetResponse:
        """Creates a dataset."""
        return await self.workflow.handle_create_dataset(request)

    @rpc_errors
    async def DeleteDataset(
        self, request: datasets_v1_dataset_service_pb2.DeleteDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_service_pb2.DeleteDatasetResponse:
        """Deletes a dataset."""
        return await self.workflow.handle_delete_dataset(request)

    @rpc_errors
    @retry_transient
    async def GetDataset(
        self, request: datasets_v1_dataset_service_pb2.GetDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_service_pb2.GetDatasetResponse:
        """Returns a dataset."""
        return await self.workflow.handle_get_dataset(request)

    @rpc_errors
    @retry_transient
    async def ListDatasets(
        self, request: datasets_v1_dataset_service_pb2.ListDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_service_pb2.ListDatasetsResponse:
        """Lists datasets a page at a time."""
        return await self.workflow.handle_list_datasets(request)

    @rpc_errors
    @retry_transient
    async def SearchDatasets(
        self, request: datasets_v1_dataset_service_pb2.SearchDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_service_pb2.SearchDatasetsResponse:
        """Lists datasets a page at a time."""
        return await self.workflow.handle_search_datasets(request)

    @rpc_errors
    async def UpdateDataset(
        self, request: datasets_v1_dataset_service_pb2.UpdateDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_service_pb2.UpdateDatasetResponse:
        """Changes a dataset."""
        return await self.workflow.handle_update_dataset(request)

    @stream_errors
    async def WatchDatasets(
        self, request: datasets_v1_dataset_service_pb2.WatchDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datasets_v1_dataset_service_pb2.WatchDatasetsResponse]:
        """Streams the changes of datasets as they happen."""
        response = await self.workflow.handle_watch_datasets(request)
        for item in messages((response,)):
            yield item
