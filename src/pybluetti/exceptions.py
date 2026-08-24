"""Exceptions raised by the pybluetti client."""

from typing import Any


class ApplicationRuntimeException(Exception):
    """Raised when a BLUETTI cloud API call fails."""

    message: str = "An unknown error has occurred."
    msgCode: int
    data: dict[str, Any] | str | None = None

    def __init__(
        self, msgCode: int, data: dict[str, Any] | str | None = None, errMessage: str | None = None
    ) -> None:
        self.msgCode = msgCode
        self.data = data

        if errMessage is not None:
            self.message = errMessage

        super().__init__(self.message)
