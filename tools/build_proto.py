"""Compile the vendored APIs into the ignored build directory; never edit generated bindings."""

import subprocess
import sys
from importlib.resources import files
from pathlib import Path


def generate() -> None:
    root = Path(__file__).resolve().parents[1]
    destination = root / "build" / "generated"
    destination.mkdir(parents=True, exist_ok=True)
    protos = sorted(str(path.relative_to(root / "proto")) for path in (root / "proto").rglob("*.proto"))
    subprocess.run([
        sys.executable, "-m", "grpc_tools.protoc", "-Iproto", "-I" + str(files("grpc_tools") / "_proto"),
        "--python_out=build/generated", "--pyi_out=build/generated", "--grpc_python_out=build/generated", *protos,
    ], cwd=root, check=True)
    for folder in sorted(destination.rglob("*")):
        if folder.is_dir() and "__pycache__" not in folder.parts:
            (folder / "__init__.py").write_text('"""Acme API bindings, built from proto/."""\n')


if __name__ == "__main__":
    generate()
