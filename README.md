# protomap-test-python

A synthetic Python code base for testing [ProtoMap](https://protomap.ai) by [HoundDog.ai](https://hounddog.ai). It is
part of the code of Acme, a fictional company.

The code mixes in, on purpose, what makes static analysis of real code bases hard, and `expected.json` is the answer key
of what a scanner should find in it.

Acme's code is spread over multiple repositories, one per programming language. They were generated together from one
catalog of Acme's APIs. Each owns its own domains and calls the others' services, so it holds copies of the protobuf
files it needs from them, byte for byte as their owners have them. Scan them together to follow calls and data from one
repository to another.

| Repository                                                                         | Language   |
|------------------------------------------------------------------------------------|------------|
| [protomap-test-csharp](https://github.com/hounddogai/protomap-test-csharp)         | C#         |
| [protomap-test-golang](https://github.com/hounddogai/protomap-test-golang)         | Go         |
| [protomap-test-java](https://github.com/hounddogai/protomap-test-java)             | Java       |
| [protomap-test-javascript](https://github.com/hounddogai/protomap-test-javascript) | JavaScript |
| [protomap-test-kotlin](https://github.com/hounddogai/protomap-test-kotlin)         | Kotlin     |
| **protomap-test-python** (this one)                                                | Python     |
| [protomap-test-rust](https://github.com/hounddogai/protomap-test-rust)             | Rust       |
| [protomap-test-swift](https://github.com/hounddogai/protomap-test-swift)           | Swift      |
| [protomap-test-typescript](https://github.com/hounddogai/protomap-test-typescript) | TypeScript |

## Repository Layout

A Python 3.12+ package under `src/acme_data` that separates each domain's transport handlers, workflows, typed mappers,
ports, and SQLAlchemy repositories. Domain packages vary between class handlers, mixins, dataclass services, and
module-level operations. A provider container supplies clients and database sessions.

The `acme-data` entry point registers every service on a `grpc.aio` server behind identity authentication, starts the
event bus consumer, and drains work on shutdown. Separate reconciliation, streaming index, and admin programs call the
same APIs.

## Build and Run

Create a virtual environment, install the package with its development dependencies, then check types and run the tests:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m mypy
.venv/bin/python -m unittest discover -s tests
```

The build backend runs `python -m grpc_tools.protoc` on the protobuf files in `proto/` and packages the `_pb2`,
`_pb2_grpc`, and `.pyi` files from `build/generated/`, which Git ignores. Run `.venv/bin/python tools/build_proto.py`
after editing a protobuf file. The tests exercise every handler with populated protobuf messages, a real loopback gRPC
server, and database writes.

`ACME_MESH`, `ACME_LISTEN`, `ACME_DATABASE_URL`, and `ACME_SERVICE_TOKEN`, the credential of the server's own calls,
configure a deployment. Locally, the database is `db.sqlite3`, which Git ignores.
