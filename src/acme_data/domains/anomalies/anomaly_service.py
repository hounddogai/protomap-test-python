"""Manages anomalies: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.anomalies.v1 import anomaly_service_pb2_grpc as anomalies_v1_anomaly_service_pb2_grpc

from acme_data.domains.anomalies.anomaly_service_workflow import AnomalyServicerWorkflow
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnomalyServicer(anomalies_v1_anomaly_service_pb2_grpc.AnomalyServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = AnomalyServicerWorkflow(deps)

    @rpc_errors
    async def BatchCreateAnomalies(
        self, requests: AsyncIterator[
            anomalies_v1_anomaly_service_pb2.BatchCreateAnomaliesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_service_pb2.BatchCreateAnomaliesResponse:
        """Takes a stream of anomalies and answers once at the end."""
        response = anomalies_v1_anomaly_service_pb2.BatchCreateAnomaliesResponse()
        async for request in requests:
            response.MergeFrom(await self.workflow.handle_batch_create_anomalies(request))
        return response

    @rpc_errors
    @retry_transient
    async def BatchGetAnomalies(
        self, request: anomalies_v1_anomaly_service_pb2.BatchGetAnomaliesRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_service_pb2.BatchGetAnomaliesResponse:
        """Returns several anomalies at once."""
        return await self.workflow.handle_batch_get_anomalies(request)

    @rpc_errors
    async def CreateAnomaly(
        self, request: anomalies_v1_anomaly_service_pb2.CreateAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_service_pb2.CreateAnomalyResponse:
        """Creates an anomaly."""
        return await self.workflow.handle_create_anomaly(request)

    @rpc_errors
    @retry_transient
    async def GetAnomaly(
        self, request: anomalies_v1_anomaly_service_pb2.GetAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_service_pb2.GetAnomalyResponse:
        """Returns an anomaly."""
        return await self.workflow.handle_get_anomaly(request)

    @rpc_errors
    @retry_transient
    async def SearchAnomalies(
        self, request: anomalies_v1_anomaly_service_pb2.SearchAnomaliesRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_service_pb2.SearchAnomaliesResponse:
        """Lists anomalies a page at a time."""
        return await self.workflow.handle_search_anomalies(request)

    @rpc_errors
    async def UpdateAnomaly(
        self, request: anomalies_v1_anomaly_service_pb2.UpdateAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_service_pb2.UpdateAnomalyResponse:
        """Changes an anomaly."""
        return await self.workflow.handle_update_anomaly(request)
