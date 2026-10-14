"""Exercise concrete handlers, oracle field mappings, transport cardinalities, and SQLAlchemy transactions."""

from __future__ import annotations

import asyncio
import importlib
import json
import logging
import os
import unittest
from collections import defaultdict
from collections.abc import AsyncIterator, Callable, Iterable
from contextlib import suppress
from pathlib import Path
from typing import Any
from unittest.mock import patch

import grpc
from google.protobuf import descriptor_pool, message_factory
from google.protobuf.descriptor import Descriptor, FieldDescriptor, MethodDescriptor, ServiceDescriptor
from google.protobuf.message import Message
from sqlalchemy import func, select

from acme_data.platform.config import Settings
from acme_data.platform.container import Container
from acme_data.platform.events import EventBus
from acme_data.platform.identity import CallerCredentials, IdentityInterceptor, caller, credential_interceptors
from acme_data.platform.persistence import AuditRecord, Repository, Snapshot
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.server import register_all

ROOT = Path(__file__).resolve().parents[1]
ORACLE = json.loads((ROOT / "expected.json").read_text())
POOL = descriptor_pool.Default()
WORKLOAD_TOKEN = 'workload-token'


def populate(message: Message, marker: str, variant: int, depth: int = 0, prefix: str = '') -> Message:
    """Build non-default messages independently of the source emitter, including every collection and oneof."""
    if depth > 5:
        return message
    full_name = message.DESCRIPTOR.full_name
    prefix = prefix or full_name
    if full_name == 'google.protobuf.Any':
        return message
    if full_name in ('google.protobuf.Timestamp', 'google.protobuf.Duration'):
        message.seconds = 10
        return message
    if full_name == 'google.protobuf.Struct':
        message.update({'source': marker})
        return message
    if full_name == 'google.protobuf.FieldMask':
        message.paths.append('name')
        return message
    selected = {oneof.name: oneof.fields[variant % len(oneof.fields)].name for oneof in message.DESCRIPTOR.oneofs}
    for field in message.DESCRIPTOR.fields:
        if field.containing_oneof and selected[field.containing_oneof.name] != field.name:
            continue
        value = getattr(message, field.name)
        location = prefix + '.' + field.name
        if field.message_type and field.message_type.GetOptions().map_entry:
            entry = field.message_type.fields_by_name['value']
            if entry.message_type:
                populate(value['primary'], marker, variant, depth + 1, location + '[primary]')
            else:
                value['primary'] = scalar(entry, marker, location)
        elif field.is_repeated:
            if field.message_type:
                for index in range(2):
                    populate(value.add(), marker, variant, depth + 1, location + f'[{index}]')
            else:
                value.extend(scalar(field, marker, location + f'[{index}]') for index in range(2))
        elif field.message_type:
            populate(value, marker, variant, depth + 1, location)
        else:
            setattr(message, field.name, scalar(field, marker, location))
    if 'page_info' in message.DESCRIPTOR.fields_by_name:
        message.page_info.next_page_token = ''
    return message


def scalar(field: FieldDescriptor, marker: str, location: str) -> Any:
    if field.type == FieldDescriptor.TYPE_STRING:
        return marker + ':' + location
    if field.type == FieldDescriptor.TYPE_BYTES:
        return (marker + ':' + location).encode()
    if field.type == FieldDescriptor.TYPE_BOOL:
        return True
    if field.type == FieldDescriptor.TYPE_ENUM:
        return field.enum_type.values[1].number
    if field.type in (FieldDescriptor.TYPE_FLOAT, FieldDescriptor.TYPE_DOUBLE):
        return sum(location.encode()) / 8
    return sum((marker + location).encode())


def message_type(descriptor: Descriptor) -> type[Message]:
    return message_factory.GetMessageClass(descriptor)


def values(message: Message, path: list[str]) -> list[Any]:
    if not path:
        return [message]
    field_name = path[0].rsplit('.', 1)[1]
    field = message.DESCRIPTOR.fields_by_name[field_name]
    if field.containing_oneof and message.WhichOneof(field.containing_oneof.name) != field.name:
        return []
    value = getattr(message, field_name)
    is_map = field.message_type and field.message_type.GetOptions().map_entry
    if len(path) == 1:
        if is_map:
            return [dict(value)]
        if field.is_repeated:
            return [list(value)]
        return [value]
    if is_map:
        return [found for child in value.values() for found in values(child, path[1:])]
    if field.is_repeated:
        return [found for child in value for found in values(child, path[1:])]
    return values(value, path[1:])


def normalized(value: Any) -> Any:
    if isinstance(value, Message):
        return value.SerializeToString(deterministic=True)
    if isinstance(value, (list, tuple)):
        return tuple(normalized(item) for item in value)
    if isinstance(value, dict):
        return {key: normalized(item) for key, item in value.items()}
    return value


def contains(target: Any, source: Any) -> bool:
    target, source = normalized(target), normalized(source)
    if target == source:
        return True
    if isinstance(target, tuple):
        if isinstance(source, tuple):
            return all(item in target for item in source)
        return source in target
    if isinstance(target, dict) and isinstance(source, dict):
        return all(target.get(key) == value for key, value in source.items())
    return False


def stub_type(service: ServiceDescriptor) -> type[Any]:
    module = service.file.name.removesuffix('.proto').replace('/', '.') + '_pb2_grpc'
    return getattr(importlib.import_module(module), service.name + 'Stub')


class Mesh:
    """The fake transport still serializes requests and returns real protobuf responses."""
    def __init__(self) -> None:
        self.requests: dict[str, list[Message]] = defaultdict(list)
        self.responses: dict[str, list[Message]] = defaultdict(list)
        self.only_response: str | None = None
        self.variant = 0
        self.paginate = False
        self.auth_method = ORACLE['aggregates'][0]['to']

    def clear(self, variant: int = 0) -> None:
        self.requests.clear()
        self.responses.clear()
        self.variant = variant
        self.only_response = None

    async def __aenter__(self) -> Mesh:
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None

    def exchange(self, path: str, request: Message, metadata: Any = None) -> Message:
        fqn = path.lstrip('/')
        service_name, method_name = fqn.split('/')
        descriptor = POOL.FindServiceByName(service_name).methods_by_name[method_name]
        snapshot = message_type(descriptor.input_type).FromString(request.SerializeToString(deterministic=True))
        self.requests[fqn].append(snapshot)
        response = message_type(descriptor.output_type)()
        if self.only_response is None or self.only_response == fqn:
            populate(response, 'reply', self.variant)
        if self.paginate and 'page_info' in response.DESCRIPTOR.fields_by_name:
            response.page_info.next_page_token = 'cursor:' + fqn if len(self.requests[fqn]) == 1 else ''
        self.responses[fqn].append(response)
        return response

    def unary_unary(self, path: str, **options: Any) -> Callable[..., Any]:
        async def call(request: Message, **kwargs: Any) -> Message:
            return self.exchange(path, request, kwargs.get('metadata'))
        return call

    def unary_stream(self, path: str, **options: Any) -> Callable[..., Any]:
        async def call(request: Message, **kwargs: Any) -> AsyncIterator[Message]:
            yield self.exchange(path, request)
        return call

    def stream_unary(self, path: str, **options: Any) -> Callable[..., Any]:
        async def call(requests: AsyncIterator[Message], **kwargs: Any) -> Message:
            result = None
            async for request in requests:
                result = self.exchange(path, request)
            if result is None:
                raise AssertionError('client stream unexpectedly empty')
            return result
        return call

    def stream_stream(self, path: str, **options: Any) -> Callable[..., Any]:
        async def call(requests: AsyncIterator[Message], **kwargs: Any) -> AsyncIterator[Message]:
            async for request in requests:
                yield self.exchange(path, request)
        return call


def rejected(code: grpc.StatusCode, details: str) -> grpc.aio.AioRpcError:
    return grpc.aio.AioRpcError(code, grpc.aio.Metadata(), grpc.aio.Metadata(), details)


class Identity(Mesh):
    """The identity service as the Go monolith serves it to this server's lookups, which must bear the workload
    credential and the tenant of their request, and name a service account. It answers the record of the id it was
    asked about, and its status."""
    def __init__(self) -> None:
        super().__init__()
        self.status = 'ok'

    def exchange(self, path: str, request: Message, metadata: Any = None) -> Message:
        headers = dict(metadata or ())
        tenant = request.context.tenant_id
        if headers.get('authorization') != 'Bearer ' + WORKLOAD_TOKEN:
            raise rejected(grpc.StatusCode.UNAUTHENTICATED, 'missing bearer token')
        if not tenant or headers.get('x-tenant-id') != tenant:
            raise rejected(grpc.StatusCode.UNAUTHENTICATED, 'missing tenant')
        if not request.context.actor.service_account:
            raise rejected(grpc.StatusCode.UNAUTHENTICATED, 'context.actor is required')
        response = super().exchange(path, request, metadata)
        key = next(field.name for field in request.DESCRIPTOR.fields if field.name.endswith('_id'))
        record = next(field.name for field in response.DESCRIPTOR.fields
                      if field.message_type and key in field.message_type.fields_by_name)
        setattr(getattr(response, record), key, getattr(request, key))
        response.result.status = self.status
        return response


class Context:
    async def abort(self, code: grpc.StatusCode, details: str) -> None:
        raise AssertionError(f'handler aborted with {code}: {details}')


async def discard_write(self: Repository, *args: Any, **kwargs: Any) -> None:
    return None


class RuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_running_loop().set_debug(False)
        logging.disable(logging.CRITICAL)
        self.mesh = Mesh()
        self.identity = Identity()
        self.settings = Settings(database_url='sqlite+aiosqlite:///:memory:', timeout=30,
                                 service_token=WORKLOAD_TOKEN)
        self.container = Container(self.settings, self.mesh)
        await self.container.initialize()
        self.interceptor = IdentityInterceptor(self.identity_stub(), self.settings)
        self.server = grpc.aio.server(interceptors=[self.interceptor])
        self.handlers = register_all(self.server, self.container)
        self.worker = asyncio.create_task(self.container.bus.consume())
        self.flows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for flow in ORACLE['flows']:
            if 'handler' in flow['island']:
                self.flows[flow['island']['handler']].append(flow)
        self.methods = [(item['name'], method) for item in ORACLE['services'] if item['implemented']
                        for method in POOL.FindServiceByName(item['name']).methods]

    def identity_stub(self) -> Any:
        return stub_type(POOL.FindServiceByName(self.identity.auth_method.split('/')[0]))(self.identity)

    async def asyncTearDown(self) -> None:
        await self.server.stop(0)
        self.worker.cancel()
        with suppress(asyncio.CancelledError):
            await self.worker
        await self.container.close()
        logging.disable(logging.NOTSET)

    async def invoke(self, service: str, method: MethodDescriptor, request: Message) -> list[Message]:
        handler = getattr(self.handlers[service], method.name)
        argument = async_messages((request,)) if method.client_streaming else request
        if method.server_streaming:
            responses = [item async for item in handler(argument, Context())]
        else:
            responses = [await handler(argument, Context())]
        for response in responses:
            self.assertEqual(response.DESCRIPTOR, method.output_type)
            response.SerializeToString(deterministic=True)
        return responses

    def assert_flow(self, flow: dict[str, Any], sources: Iterable[Message], targets: Iterable[Message]) -> None:
        expected = [value for source in sources for value in values(source, flow['source']['path'])]
        actual = [value for target in targets for value in values(target, flow['target']['path'])]
        for source in expected:
            self.assertTrue(any(contains(target, source) for target in actual),
                            f"{flow['id']} {flow['pattern']}: {flow['source']} -> {flow['target']}")

    async def test_every_handler_carries_request_and_response_fields(self) -> None:
        self.assertEqual(len(self.handlers), 240)
        self.assertEqual(len(self.methods), len(ORACLE['handlers']))
        exercised = set()
        observed_calls = set()
        with patch.object(Repository, 'audit', discard_write), patch.object(Repository, 'save', discard_write):
            for variant in range(3):
                for service, method in self.methods:
                    fqn = service + '/' + method.name
                    with self.subTest(method=fqn, variant=variant):
                        self.mesh.clear(variant)
                        request = populate(message_type(method.input_type)(), 'input', variant)
                        responses = await self.invoke(service, method, request)
                        observed_calls.update((fqn, target) for target in self.mesh.requests)
                        for flow in self.flows[fqn]:
                            if flow['target']['kind'] == 'call_request':
                                sources = [request] if flow['source']['kind'] == 'handler_request' else \
                                    self.mesh.responses[flow['source']['method']]
                                targets = self.mesh.requests[flow['target']['method']]
                                if not targets:
                                    # An inactive oneof may leave a fan-out with no elements in this variant.
                                    continue
                                self.assert_flow(flow, sources, targets)
                                if any(values(source, flow['source']['path']) for source in sources):
                                    exercised.add(flow['id'])
                            elif flow['pattern'] == 'echo':
                                self.assert_flow(flow, [request], responses)
                                exercised.add(flow['id'])
                        self.assertEqual(tenant_id.get(), '')
        self.assertGreater(len(exercised), 10000)
        planned_calls = {(call['from']['handler'], call['to']) for call in ORACLE['calls']
                         if 'handler' in call['from']}
        self.assertEqual(observed_calls, planned_calls)

    async def test_each_downstream_response_contributes_to_the_handler(self) -> None:
        count = 0
        with patch.object(Repository, 'audit', discard_write), patch.object(Repository, 'save', discard_write):
            for service, method in self.methods:
                fqn = service + '/' + method.name
                returning: dict[str, list[dict[str, Any]]] = defaultdict(list)
                for flow in self.flows[fqn]:
                    if flow['source']['kind'] == 'call_response' and flow['target']['kind'] == 'handler_response':
                        returning[flow['source']['method']].append(flow)
                for downstream, flows in sorted(returning.items()):
                    with self.subTest(method=fqn, downstream=downstream):
                        self.mesh.clear()
                        self.mesh.only_response = downstream
                        request = populate(message_type(method.input_type)(), 'input', 0)
                        responses = await self.invoke(service, method, request)
                        for flow in flows:
                            self.assert_flow(flow, self.mesh.responses[downstream], responses)
                            count += 1
        self.assertGreater(count, 3000)

    async def test_loopback_authenticates_all_four_rpc_cardinalities(self) -> None:
        port = self.server.add_insecure_port('127.0.0.1:0')
        await self.server.start()
        selected = {}
        for service, method in self.methods:
            selected.setdefault((method.client_streaming, method.server_streaming), (service, method))
        self.assertEqual(len(selected), 4)
        metadata = (('authorization', 'Bearer test'), ('x-tenant-id', 'input'))
        async with grpc.aio.insecure_channel(f'127.0.0.1:{port}') as channel:
            for (client_streaming, server_streaming), (service, method) in sorted(selected.items()):
                request = populate(message_type(method.input_type)(), 'input', 0)
                stub = stub_type(POOL.FindServiceByName(service))(channel)
                invoke = getattr(stub, method.name)
                for allowed in (False, True):
                    argument = async_messages((request, request)) if client_streaming else request
                    call = invoke(argument, timeout=30, metadata=metadata if allowed else ())
                    if not allowed:
                        with self.assertRaises(grpc.aio.AioRpcError) as error:
                            if server_streaming:
                                await anext(call.__aiter__())
                            else:
                                await call
                        self.assertEqual(error.exception.code(), grpc.StatusCode.UNAUTHENTICATED)
                    elif server_streaming:
                        self.assertTrue([message async for message in call])
                    else:
                        self.assertIsInstance(await call, Message)
            self.assertGreaterEqual(len(self.identity.requests[self.identity.auth_method]), 4)
            # Identity's answer accepts the caller only with its status, for the token asked about.
            service, method = selected[(False, False)]
            invoke = getattr(stub_type(POOL.FindServiceByName(service))(channel), method.name)
            self.identity.status = 'revoked'
            with self.assertRaises(grpc.aio.AioRpcError) as error:
                await invoke(populate(message_type(method.input_type)(), 'input', 0), timeout=30, metadata=metadata)
            self.assertEqual(error.exception.code(), grpc.StatusCode.PERMISSION_DENIED)

    async def test_loopback_handlers_call_protected_services_with_their_callers_credentials(self) -> None:
        """A handler's calls of this server's services pass their identity checks with the credentials of its caller."""
        implemented = {item['name'] for item in ORACLE['services'] if item['implemented']}
        planned: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for call in ORACLE['calls']:
            if 'handler' in call['from']:
                planned[call['from']['handler']].append(call)
        fqn = min(handler for handler, calls in planned.items()
                  if all(call['to'].split('/')[0] in implemented and call['to'] not in planned
                         and call['pattern'] != 'event_bus' for call in calls))
        server = grpc.aio.server(interceptors=[self.interceptor])
        port = server.add_insecure_port('127.0.0.1:0')
        address = f'127.0.0.1:{port}'
        with patch.object(Repository, 'audit', discard_write), patch.object(Repository, 'save', discard_write):
            async with grpc.aio.insecure_channel(address, interceptors=credential_interceptors(self.settings)) as mesh:
                container = Container(self.settings, mesh)
                await container.initialize()
                register_all(server, container)
                await server.start()
                try:
                    service_name, method_name = fqn.split('/')
                    service = POOL.FindServiceByName(service_name)
                    method = service.methods_by_name[method_name]
                    request = populate(message_type(method.input_type)(), 'input', 0)
                    async with grpc.aio.insecure_channel(address) as channel:
                        invoke = getattr(stub_type(service)(channel), method_name)
                        argument = async_messages((request,)) if method.client_streaming else request
                        call = invoke(argument, timeout=30, metadata=(('authorization', 'Bearer caller-token'),
                                                                      ('x-tenant-id', 'tenant-a')))
                        if method.server_streaming:
                            self.assertTrue([message async for message in call])
                        else:
                            self.assertIsInstance(await call, Message)
                finally:
                    await server.stop(0)
                    await container.close()
        # One lookup for the call of the handler, and one for each call it makes, all of its caller's token.
        lookups = self.identity.requests[self.identity.auth_method]
        key = next(field.name for field in lookups[0].DESCRIPTOR.fields if field.name.endswith('_id'))
        self.assertGreater(len(lookups), 1, fqn)
        self.assertEqual({(getattr(lookup, key), lookup.context.tenant_id) for lookup in lookups},
                         {('caller-token', 'tenant-a')})

    async def test_loopback_calls_of_every_cardinality_carry_credentials(self) -> None:
        """A channel of the server signs its calls of all four cardinalities, with the credentials of the call their
        handler serves, or else with the server's own."""
        seen: dict[str, list[dict[str, str]]] = defaultdict(list)

        def record(name: str, context: grpc.aio.ServicerContext) -> None:
            seen[name].append({key: str(value) for key, value in context.invocation_metadata() or ()})

        async def unary_unary(request: bytes, context: grpc.aio.ServicerContext) -> bytes:
            record('unary_unary', context)
            return request

        async def unary_stream(request: bytes, context: grpc.aio.ServicerContext) -> AsyncIterator[bytes]:
            record('unary_stream', context)
            yield request

        async def stream_unary(requests: AsyncIterator[bytes], context: grpc.aio.ServicerContext) -> bytes:
            record('stream_unary', context)
            return b''.join([request async for request in requests])

        async def stream_stream(requests: AsyncIterator[bytes],
                                context: grpc.aio.ServicerContext) -> AsyncIterator[bytes]:
            record('stream_stream', context)
            async for request in requests:
                yield request

        server = grpc.aio.server()
        server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler('acme.test.v1.Probe', {
            'UnaryUnary': grpc.unary_unary_rpc_method_handler(unary_unary),
            'UnaryStream': grpc.unary_stream_rpc_method_handler(unary_stream),
            'StreamUnary': grpc.stream_unary_rpc_method_handler(stream_unary),
            'StreamStream': grpc.stream_stream_rpc_method_handler(stream_stream),
        }),))
        port = server.add_insecure_port('127.0.0.1:0')
        await server.start()
        try:
            async with grpc.aio.insecure_channel(f'127.0.0.1:{port}',
                                                 interceptors=credential_interceptors(self.settings)) as channel:
                for credentials in ((('authorization', 'Bearer caller-token'), ('x-tenant-id', 'tenant-a')), ()):
                    token = caller.set(credentials)
                    try:
                        await channel.unary_unary('/acme.test.v1.Probe/UnaryUnary')(b'probe', timeout=10)
                        self.assertEqual([reply async for reply in channel.unary_stream(
                            '/acme.test.v1.Probe/UnaryStream')(b'probe', timeout=10)], [b'probe'])
                        await channel.stream_unary('/acme.test.v1.Probe/StreamUnary')(
                            async_messages((b'probe',)), timeout=10)
                        self.assertEqual([reply async for reply in channel.stream_stream(
                            '/acme.test.v1.Probe/StreamStream')(async_messages((b'probe',)), timeout=10)], [b'probe'])
                    finally:
                        caller.reset(token)
        finally:
            await server.stop(0)
        self.assertEqual(sorted(seen), ['stream_stream', 'stream_unary', 'unary_stream', 'unary_unary'])
        for cardinality, calls in sorted(seen.items()):
            with self.subTest(cardinality=cardinality):
                self.assertEqual([call.get('authorization') for call in calls],
                                 ['Bearer caller-token', 'Bearer ' + WORKLOAD_TOKEN])
                self.assertEqual(calls[0].get('x-tenant-id'), 'tenant-a')

    def test_calls_carry_the_callers_credentials_or_else_the_workloads(self) -> None:
        signing = CallerCredentials(self.settings)
        details = grpc.aio.ClientCallDetails('/acme.test.v1.Test/Call', None, None, None, None)
        request = type('Request', (), {'context': type('Context', (), {'tenant_id': 'tenant-b'})()})()
        self.assertEqual(list(signing.sign(details, request).metadata),
                         [('authorization', 'Bearer ' + WORKLOAD_TOKEN), ('x-tenant-id', 'tenant-b')])
        token = caller.set((('authorization', 'Bearer caller-token'), ('x-tenant-id', 'tenant-a')))
        try:
            self.assertEqual(list(signing.sign(details, request).metadata),
                             [('authorization', 'Bearer caller-token'), ('x-tenant-id', 'tenant-a')])
        finally:
            caller.reset(token)
        own = details._replace(metadata=(('authorization', 'Bearer program'),))
        self.assertIs(signing.sign(own, request), own)

    async def test_event_bus_serves_requests_its_deliveries_make(self) -> None:
        """A delivery's RPC may reach a handler that makes a request of the bus in turn, as
        TerminateCohort's does through ResolveAnalyticsEvents, and both must be served."""
        bus = EventBus(1)
        context_type = message_type(POOL.FindMessageTypeByName('acme.common.v1.RequestContext'))

        async def outer(payload: Message) -> Message:
            return await bus.request('inner', payload, 5)

        async def inner(payload: Message) -> Message:
            reply = context_type()
            reply.CopyFrom(payload)
            reply.trace_id = 'inner:' + caller.get()[0][1]
            return reply

        bus.subscribe('outer', outer)
        bus.subscribe('inner', inner)
        worker = asyncio.create_task(bus.consume())
        token = caller.set((('authorization', 'Bearer caller-token'), ('x-tenant-id', 'tenant-a')))
        try:
            reply = await bus.request('outer', context_type(tenant_id='tenant-a'), 5)
        finally:
            caller.reset(token)
            worker.cancel()
            with suppress(asyncio.CancelledError):
                await worker
        self.assertEqual(reply.tenant_id, 'tenant-a')
        self.assertEqual(reply.trace_id, 'inner:Bearer caller-token')

    async def test_sqlalchemy_repository_commits_audit_and_snapshot(self) -> None:
        repository = Repository('datasets', self.container.sessions)
        await repository.audit('tenant', 'CreateDataset', {'classification': 'internal'})
        await repository.save('tenant', 'Dataset', 'dataset-1', b'first')
        await repository.save('tenant', 'Dataset', 'dataset-1', b'updated')
        async with self.container.sessions() as session:
            count = await session.scalar(select(func.count()).select_from(AuditRecord))
            snapshot = await session.get(Snapshot, ('datasets', 'tenant', 'Dataset', 'dataset-1'))
            self.assertEqual(count, 1)
            self.assertIsNotNone(snapshot)
            self.assertEqual(snapshot.payload, b'updated')

    async def test_programs_execute_batch_and_stream_calls(self) -> None:
        from acme_data.programs import indexer, reconcile
        self.mesh.paginate = True
        with patch('grpc.aio.insecure_channel', return_value=self.mesh), \
                patch.dict(os.environ, {'ACME_TOKEN': 'test', 'ACME_USER': 'operator'}):
            await reconcile.run('mesh', 'input')
            await indexer.run('mesh', 'input')
        for flow in ORACLE['flows']:
            if flow['pattern'] in ('program_batch', 'program_stream'):
                self.assert_flow(flow, self.mesh.responses[flow['source']['method']],
                                 self.mesh.requests[flow['target']['method']])
        # The servers downstream reject a request whose context names no actor.
        self.assertEqual({request.context.actor.user_id for requests in self.mesh.requests.values()
                          for request in requests}, {'operator'})


if __name__ == '__main__':
    unittest.main()
