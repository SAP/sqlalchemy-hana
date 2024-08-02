"""SAP HANA types."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Callable, Literal, TypeVar, overload
from uuid import UUID as PyUUID

import sqlalchemy
from sqlalchemy import types as sqltypes
from sqlalchemy.engine import Dialect


class DATE(sqltypes.DATE):
    def literal_processor(self, dialect: Dialect) -> Callable[[date], str]:
        def process(value: date) -> str:
            return f"TO_DATE('{value}')"

        return process


class TIME(sqltypes.TIME):
    def literal_processor(self, dialect: Dialect) -> Callable[[time], str]:
        def process(value: time) -> str:
            return f"TO_TIME('{value}')"

        return process


class SECONDDATE(sqltypes.DateTime):
    __visit_name__ = "SECONDDATE"

    def literal_processor(self, dialect: Dialect) -> Callable[[datetime], str]:
        def process(value: datetime) -> str:
            return f"TO_SECONDDATE('{value}')"

        return process


class TIMESTAMP(sqltypes.TIMESTAMP):
    def literal_processor(self, dialect: Dialect) -> Callable[[datetime], str]:
        def process(value: datetime) -> str:
            return f"TO_TIMESTAMP('{value}')"

        return process


LONGDATE = TIMESTAMP


class TINYINT(sqltypes.Integer):
    __visit_name__ = "TINYINT"


class SMALLINT(sqltypes.Integer):
    __visit_name__ = "SMALLINT"


class INTEGER(sqltypes.INTEGER):
    pass


class BIGINT(sqltypes.BIGINT):
    pass


class DECIMAL(sqltypes.DECIMAL):  # type:ignore[type-arg]
    pass


class SMALLDECIMAL(sqltypes.Numeric):  # type:ignore[type-arg]
    __visit_name__ = "SMALLDECIMAL"

    def __init__(
        self,
        decimal_return_scale: int | None = None,
        asdecimal: Literal[True] | Literal[False] = True,
    ) -> None:
        # SMALLDECIMAL does not return scale and precision
        super().__init__(
            precision=None,
            scale=None,
            decimal_return_scale=decimal_return_scale,
            asdecimal=asdecimal,
        )


class REAL(sqltypes.REAL):  # type:ignore[type-arg]
    pass


_BaseDouble = sqltypes.FLOAT if sqlalchemy.__version__ < "2" else sqltypes.DOUBLE


class DOUBLE(_BaseDouble):  # type:ignore[valid-type,misc]
    pass


class FLOAT(sqltypes.FLOAT):  # type:ignore[type-arg]
    pass


class BOOLEAN(sqltypes.BOOLEAN):
    pass


class VARCHAR(sqltypes.VARCHAR):
    pass


class NVARCHAR(sqltypes.NVARCHAR):
    pass


class ALPHANUM(sqltypes.String):
    __visit_name__ = "ALPHANUM"

    def __init__(self, length: int | None = None, collation: str | None = None) -> None:
        if length is not None and length > 127:
            raise ValueError("Alphanum does only support a length up to 127 characters")
        super().__init__(length, collation)


class CHAR(sqltypes.CHAR):
    pass


class NCHAR(sqltypes.NCHAR):
    pass


class VARBINARY(sqltypes.VARBINARY):
    pass


class BLOB(sqltypes.BLOB):
    pass


class CLOB(sqltypes.CLOB):
    pass


class NCLOB(sqltypes.UnicodeText):
    __visit_name__ = "NCLOB"


class JSON(sqltypes.JSON):
    pass


_UUID_RETURN = TypeVar("_UUID_RETURN", str, PyUUID)


class Uuid(sqltypes.Uuid[_UUID_RETURN]):

    @overload
    def __init__(
        self,
        as_uuid: Literal[True] = ...,
        native_uuid: bool = ...,
        as_varbinary: bool = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        as_uuid: Literal[False] = ...,
        native_uuid: bool = ...,
        as_varbinary: bool = ...,
    ) -> None: ...

    def __init__(
        self,
        as_uuid: bool = True,
        native_uuid: bool = False,
        as_varbinary: bool = False,
    ) -> None:
        if native_uuid:
            raise ValueError("native_uuid is not supported by SAP HANA")
        super().__init__(as_uuid, native_uuid)
        self.as_varbinary = as_varbinary

    def bind_processor(self, dialect: Dialect) -> Callable[[Any], str | bytes]:
        if not self.as_varbinary:
            return super().bind_processor(dialect)

        def process(value: _UUID_RETURN | None) -> str | bytes:
            if value is None:
                return value
            uuid = value if isinstance(value, PyUUID) else PyUUID(value)
            return uuid.bytes

        return process

    def result_processor(
        self, dialect: Dialect, coltype: Any
    ) -> Callable[[Any], _UUID_RETURN | None]:
        if not self.as_varbinary:
            return super().result_processor(dialect, coltype)

        def process(value: memoryview | None) -> _UUID_RETURN | None:
            if value is None:
                return value
            if self.as_uuid:
                return PyUUID(bytes=value.tobytes())
            return str(PyUUID(bytes=value.tobytes()))

        return process

    def literal_processor(self, dialect: Dialect) -> Callable[[Any], str]:
        if not self.as_varbinary:
            return super().literal_processor(dialect)

        def process(value: _UUID_RETURN) -> str:
            uuid = value if isinstance(value, PyUUID) else PyUUID(value)
            return f"""'{uuid.bytes}'"""

        return process


__all__ = (
    "ALPHANUM",
    "BIGINT",
    "BLOB",
    "BOOLEAN",
    "CHAR",
    "CLOB",
    "DATE",
    "DECIMAL",
    "DOUBLE",
    "FLOAT",
    "INTEGER",
    "JSON",
    "LONGDATE",
    "NCHAR",
    "NCLOB",
    "NVARCHAR",
    "REAL",
    "SECONDDATE",
    "SMALLDECIMAL",
    "SMALLINT",
    "TIME",
    "TIMESTAMP",
    "TINYINT",
    "VARBINARY",
    "VARCHAR",
    "Uuid",
)
