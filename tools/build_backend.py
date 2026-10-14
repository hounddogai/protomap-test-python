"""PEP 517/660 hooks: wheels, sdists, and editable installs share protobuf generation."""

from typing import Any

from setuptools import build_meta as backend

from build_proto import generate

get_requires_for_build_wheel = backend.get_requires_for_build_wheel
get_requires_for_build_editable = backend.get_requires_for_build_editable
get_requires_for_build_sdist = backend.get_requires_for_build_sdist
prepare_metadata_for_build_wheel = backend.prepare_metadata_for_build_wheel
prepare_metadata_for_build_editable = backend.prepare_metadata_for_build_editable


def build_wheel(wheel_directory: str, config_settings: Any = None, metadata_directory: Any = None) -> str:
    generate()
    return backend.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_editable(wheel_directory: str, config_settings: Any = None, metadata_directory: Any = None) -> str:
    generate()
    return backend.build_editable(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory: str, config_settings: Any = None) -> str:
    return backend.build_sdist(sdist_directory, config_settings)
