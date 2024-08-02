"""UUID type."""

from __future__ import annotations

from typing import Any, Callable, TypeVar
from uuid import UUID as PyUUID

from sqlalchemy import types as sqltypes
from sqlalchemy.engine import Dialect

_RET = TypeVar("_RET", str, PyUUID)


class Uuid(sqltypes.Uuid[_RET]):

    def __init__(
        self,
        as_uuid: bool = True,
        native_uuid: bool = True,
        as_varbinary: bool = False,
    ) -> None:
        super().__init__(as_uuid, native_uuid)  # type:ignore
        self.as_varbinary = as_varbinary

    def bind_processor(self, dialect: Dialect) -> Callable[[Any | None], Any | None]:
        if not self.as_varbinary:
            return super().bind_processor(dialect)

        def process(value: Any | None) -> Any | None:
            if value is None:
                return value
            uuid = value if isinstance(value, PyUUID) else PyUUID(value)
            return uuid.bytes

        return process

    def result_processor(
        self, dialect: Dialect, coltype: Any
    ) -> Callable[[Any | None], Any | None]:
        if not self.as_varbinary:
            return super().result_processor(dialect, coltype)

        def process(value: Any | None) -> Any | None:
            if value is None:
                return value
            if self.as_uuid:
                return PyUUID(bytes=value.tobytes())
            return str(PyUUID(bytes=value.tobytes()))

        return process
