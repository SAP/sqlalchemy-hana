"""UUID type."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar
from uuid import UUID as PyUUID

from sqlalchemy import types as sqltypes
from sqlalchemy.engine import Dialect
from typing_extensions import override

_RET = TypeVar("_RET", str, PyUUID)


class Uuid(sqltypes.Uuid[_RET]):
    """SAP HANA UUID type."""

    def __init__(
        self,
        as_uuid: bool = True,
        native_uuid: bool = True,
        as_varbinary: bool = False,
    ) -> None:
        super().__init__(as_uuid, native_uuid)  # type:ignore[call-overload,misc]
        self.as_varbinary = as_varbinary

    @override
    def bind_processor(
        self, dialect: Dialect
    ) -> Callable[[Any | None], Any | None] | None:
        if not self.as_varbinary:
            return super().bind_processor(dialect)

        def _process(value: Any | None) -> Any | None:
            if value is None:
                return value
            uuid = value if isinstance(value, PyUUID) else PyUUID(value)
            return uuid.bytes

        return _process

    @override
    def result_processor(
        self, dialect: Dialect, coltype: Any
    ) -> Callable[[Any | None], Any | None]:
        if not self.as_varbinary:
            return super().result_processor(dialect, coltype)

        def _process(value: Any | None) -> Any | None:
            if value is None:
                return value
            if self.as_uuid:
                return PyUUID(bytes=value.tobytes())
            return str(PyUUID(bytes=value.tobytes()))

        return _process
