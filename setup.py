"""Package the application and the bindings prepared by our PEP 517 backend."""

from setuptools import find_packages, setup

setup(
    packages=sorted(find_packages("src") + find_packages("build/generated")),
    package_dir={"": "src", "acme": "build/generated/acme"},
    package_data={"": ["*.pyi", "py.typed"]},
)
