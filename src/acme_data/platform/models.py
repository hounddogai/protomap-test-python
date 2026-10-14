"""Validated dataclass models used by teams that expose a model_validate/model_dump interface."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import fields, is_dataclass
from typing import Self, cast, get_args, get_origin, get_type_hints


class ValidatedModel:
    @classmethod
    def model_validate(cls, values: Mapping[str, object]) -> Self:
        if not is_dataclass(cls):
            raise TypeError("validated models must declare dataclass fields")
        expected = {field.name for field in fields(cls)}
        if set(values) != expected:
            raise ValueError(f"fields do not match {cls.__name__}")
        for name, annotation in get_type_hints(cls).items():
            value = values[name]
            origin = get_origin(annotation)
            if origin is list:
                element = get_args(annotation)[0]
                if not isinstance(value, list) or not all(isinstance(item, element) for item in value):
                    raise ValueError(f"{name} requires a typed list")
            elif origin is dict:
                key_type, value_type = get_args(annotation)
                if not isinstance(value, dict) or not all(isinstance(key, key_type) and isinstance(item, value_type)
                                                          for key, item in value.items()):
                    raise ValueError(f"{name} requires a typed mapping")
            elif not isinstance(value, annotation):
                raise ValueError(f"{name} has the wrong type")
        return cast(Callable[..., Self], cls)(**dict(values))

    def model_dump(self) -> dict[str, object]:
        if not is_dataclass(self):
            raise TypeError("validated models must declare dataclass fields")
        return {field.name: getattr(self, field.name) for field in fields(self)}
