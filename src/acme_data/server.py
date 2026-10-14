"""Serve every data domain and supervise the event consumer."""

from __future__ import annotations

from contextlib import suppress
import asyncio
import logging
import signal

import grpc

from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc

from acme_data.domains.analytics import wiring as analytics
from acme_data.domains.anomalies import wiring as anomalies
from acme_data.domains.datahub import wiring as datahub
from acme_data.domains.datasets import wiring as datasets
from acme_data.domains.featurestore import wiring as featurestore
from acme_data.domains.forecasting import wiring as forecasting
from acme_data.domains.labeling import wiring as labeling
from acme_data.domains.lineage import wiring as lineage
from acme_data.domains.metrics import wiring as metrics
from acme_data.domains.modelregistry import wiring as modelregistry
from acme_data.domains.pipelines import wiring as pipelines
from acme_data.domains.recommendations import wiring as recommendations
from acme_data.platform.config import Settings
from acme_data.platform.container import Container
from acme_data.platform.identity import IdentityInterceptor
from acme_data.platform.identity import credential_interceptors
from acme_data.platform.logging import configure


def register_all(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    registered: dict[str, object] = {}
    registered.update(analytics.register(server, container))
    registered.update(anomalies.register(server, container))
    registered.update(datahub.register(server, container))
    registered.update(datasets.register(server, container))
    registered.update(featurestore.register(server, container))
    registered.update(forecasting.register(server, container))
    registered.update(labeling.register(server, container))
    registered.update(lineage.register(server, container))
    registered.update(metrics.register(server, container))
    registered.update(modelregistry.register(server, container))
    registered.update(pipelines.register(server, container))
    registered.update(recommendations.register(server, container))
    return registered


async def serve(settings: Settings) -> None:
    credentials = credential_interceptors(settings)
    async with grpc.aio.insecure_channel(settings.mesh, interceptors=credentials) as channel:
        container = Container(settings, channel)
        await container.initialize()
        interceptor = IdentityInterceptor(
            identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub(channel),
            settings
        )
        server = grpc.aio.server(interceptors=[interceptor])
        register_all(server, container)
        if server.add_insecure_port(settings.listen) == 0:
            await container.close()
            raise RuntimeError('could not bind the gRPC listener')
        worker = asyncio.create_task(container.bus.consume(), name='domain-events')
        stopped = asyncio.Event()
        loop = asyncio.get_running_loop()
        for signum in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(signum, stopped.set)
        try:
            await server.start()
            logging.getLogger(__name__).info('server ready', extra={'fields': {'listen': settings.listen}})
            await stopped.wait()
        finally:
            await server.stop(grace=5)
            with suppress(TimeoutError):
                await asyncio.wait_for(container.bus.queue.join(), timeout=5)
            worker.cancel()
            with suppress(asyncio.CancelledError):
                await worker
            await container.close()
            for signum in (signal.SIGINT, signal.SIGTERM):
                loop.remove_signal_handler(signum)


def main() -> None:
    configure()
    asyncio.run(serve(Settings.from_environment()))


if __name__ == '__main__':
    main()
