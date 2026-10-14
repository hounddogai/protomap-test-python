"""Authenticate all four gRPC cardinalities through identity, and give the calls handlers make their caller's
credentials."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any

import grpc

from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc

from acme_data.platform.config import Settings


# The credentials of the call a handler serves, which the calls it makes forward, even from the event bus,
# whose deliveries run in the context of the request that queued them.
caller: ContextVar[tuple[tuple[str, str], ...]] = ContextVar('caller', default=())


def workload(settings: Settings, tenant: str) -> tuple[tuple[str, str], ...]:
    """The credentials of this server's own calls, made for a tenant."""
    return (('authorization', 'Bearer ' + settings.service_token), ('x-tenant-id', tenant))


class IdentityInterceptor(grpc.aio.ServerInterceptor):
    def __init__(
        self,
        identity: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
        settings: Settings
    ) -> None:
        self.identity = identity
        self.settings = settings

    async def authenticate(self, context: grpc.aio.ServicerContext) -> None:
        metadata = dict(context.invocation_metadata())
        authorization = str(metadata.get('authorization', ''))
        tenant = str(metadata.get('x-tenant-id', ''))
        token = authorization.removeprefix('Bearer ')
        if not authorization.startswith('Bearer ') or not token or not tenant:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, 'a bearer token and a tenant are required')
        request = identity_v1_user_validation_service_pb2.CheckUserEligibilityRequest(
            user_id=token, context=common_v1_context_pb2.RequestContext(tenant_id=tenant),
        )
        request.context.actor.user_id = 'acme-data'
        request.context.actor.service_account = True
        request.details.strict = True
        try:
            decision = await self.identity.CheckUserEligibility(
                request, timeout=self.settings.timeout, metadata=workload(self.settings, tenant),
            )
        except grpc.aio.AioRpcError as error:
            code = error.code()
            if code not in (grpc.StatusCode.UNAUTHENTICATED, grpc.StatusCode.PERMISSION_DENIED):
                code = grpc.StatusCode.UNAVAILABLE
            await context.abort(code, 'identity check failed')
            raise
        if decision.result.status != 'ok' or decision.user.user_id != token:
            await context.abort(grpc.StatusCode.PERMISSION_DENIED, 'identity policy denied this call')
        caller.set((('authorization', authorization), ('x-tenant-id', tenant)))

    async def intercept_service(
        self, continuation: Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler | None]],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler | None:
        handler = await continuation(handler_call_details)
        if handler is None:
            return None

        async def unary_unary(request: Any, context: Any) -> Any:
            await self.authenticate(context)
            return await handler.unary_unary(request, context)

        async def unary_stream(request: Any, context: Any) -> AsyncIterator[Any]:
            await self.authenticate(context)
            async for response in handler.unary_stream(request, context):
                yield response

        async def stream_unary(requests: AsyncIterator[Any], context: Any) -> Any:
            await self.authenticate(context)
            return await handler.stream_unary(requests, context)

        async def stream_stream(requests: AsyncIterator[Any], context: Any) -> AsyncIterator[Any]:
            await self.authenticate(context)
            async for response in handler.stream_stream(requests, context):
                yield response

        options = dict(request_deserializer=handler.request_deserializer,
                       response_serializer=handler.response_serializer)
        if handler.request_streaming and handler.response_streaming:
            return grpc.stream_stream_rpc_method_handler(stream_stream, **options)
        if handler.request_streaming:
            return grpc.stream_unary_rpc_method_handler(stream_unary, **options)
        if handler.response_streaming:
            return grpc.unary_stream_rpc_method_handler(unary_stream, **options)
        return grpc.unary_unary_rpc_method_handler(unary_unary, **options)


class CallerCredentials:
    """Give every call that has no credentials of its own the credentials of the call its handler serves, or
    else, for a call no caller asked for, this server's own, for the tenant of its request.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def sign(self, details: Any, request: Any = None) -> Any:
        metadata = list(details.metadata or ())
        if any(key == 'authorization' for key, _ in metadata):
            return details
        credentials = caller.get()
        if not credentials:
            scoped = getattr(request, 'context', None)
            credentials = workload(self.settings, getattr(scoped, 'tenant_id', ''))
        return details._replace(metadata=grpc.aio.Metadata(*metadata, *credentials))


class UnaryUnaryCredentials(grpc.aio.UnaryUnaryClientInterceptor):
    """Signs the channel's unary-unary calls (see `CallerCredentials`)."""

    def __init__(self, signing: CallerCredentials) -> None:
        self.signing = signing

    async def intercept_unary_unary(self, continuation: Any, details: Any, request: Any) -> Any:
        return await continuation(self.signing.sign(details, request), request)


class UnaryStreamCredentials(grpc.aio.UnaryStreamClientInterceptor):
    """Signs the channel's unary-stream calls (see `CallerCredentials`)."""

    def __init__(self, signing: CallerCredentials) -> None:
        self.signing = signing

    async def intercept_unary_stream(self, continuation: Any, details: Any, request: Any) -> Any:
        return await continuation(self.signing.sign(details, request), request)


class StreamUnaryCredentials(grpc.aio.StreamUnaryClientInterceptor):
    """Signs the channel's stream-unary calls (see `CallerCredentials`)."""

    def __init__(self, signing: CallerCredentials) -> None:
        self.signing = signing

    async def intercept_stream_unary(self, continuation: Any, details: Any, requests: Any) -> Any:
        return await continuation(self.signing.sign(details), requests)


class StreamStreamCredentials(grpc.aio.StreamStreamClientInterceptor):
    """Signs the channel's stream-stream calls (see `CallerCredentials`)."""

    def __init__(self, signing: CallerCredentials) -> None:
        self.signing = signing

    async def intercept_stream_stream(self, continuation: Any, details: Any, requests: Any) -> Any:
        return await continuation(self.signing.sign(details), requests)


def credential_interceptors(settings: Settings) -> list[grpc.aio.ClientInterceptor]:
    """The interceptors that sign every call of a channel, of each of the four cardinalities."""
    signing = CallerCredentials(settings)
    return [UnaryUnaryCredentials(signing), UnaryStreamCredentials(signing),
            StreamUnaryCredentials(signing), StreamStreamCredentials(signing)]
