"""Shared constants for pybluetti."""

from enum import Enum


class StringEnum(str, Enum):
    """String Enum define."""

    def __str__(self) -> str:
        return str(self.value)


class Method(StringEnum):
    """HTTP Methods define."""

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
