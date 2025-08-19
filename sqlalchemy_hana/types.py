"""SAP HANA types."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import TYPE_CHECKING, Callable, Generic, Literal, TypeVar

import sqlalchemy
from sqlalchemy import types as sqltypes
from sqlalchemy.engine import Dialect
from sqlalchemy.sql.type_api import TypeEngine
from typing_extensions import override

if TYPE_CHECKING:
    StrTypeEngine = TypeEngine[str]

else:
    StrTypeEngine = TypeEngine

_RV = TypeVar("_RV", tuple[float, ...], list[float], memoryview)


class DATE(sqltypes.DATE):
    """SAP HANA DATE type."""

    @override
    def literal_processor(self, dialect: Dialect) -> Callable[[date], str]:
        def _process(value: date) -> str:
            return f"TO_DATE('{value}')"

        return _process


class TIME(sqltypes.TIME):
    """SAP HANA TIME type."""

    @override
    def literal_processor(self, dialect: Dialect) -> Callable[[time], str]:
        def _process(value: time) -> str:
            return f"TO_TIME('{value}')"

        return _process


class SECONDDATE(sqltypes.DateTime):
    """SAP HANA SECONDDATE type."""

    __visit_name__ = "SECONDDATE"

    @override
    def literal_processor(self, dialect: Dialect) -> Callable[[datetime], str]:
        def _process(value: datetime) -> str:
            return f"TO_SECONDDATE('{value}')"

        return _process


class TIMESTAMP(sqltypes.TIMESTAMP):
    """SAP HANA TIMESTAMP type."""

    @override
    def literal_processor(self, dialect: Dialect) -> Callable[[datetime], str]:
        def _process(value: datetime) -> str:
            return f"TO_TIMESTAMP('{value}')"

        return _process


LONGDATE = TIMESTAMP


class TINYINT(sqltypes.Integer):
    """SAP HANA TINYINT type."""

    __visit_name__ = "TINYINT"


class SMALLINT(sqltypes.Integer):
    """SAP HANA SMALLINT type."""

    __visit_name__ = "SMALLINT"


class INTEGER(sqltypes.INTEGER):
    """SAP HANA INTEGER type."""


class BIGINT(sqltypes.BIGINT):
    """SAP HANA BIGINT type."""


class DECIMAL(sqltypes.DECIMAL):  # type:ignore[type-arg]
    """SAP HANA DECIMAL type."""


class SMALLDECIMAL(sqltypes.Numeric):  # type:ignore[type-arg]
    """SAP HANA SMALLDECIMAL type."""

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
    """SAP HANA REAL type."""


_BaseDouble = sqltypes.FLOAT if sqlalchemy.__version__ < "2" else sqltypes.DOUBLE


class DOUBLE(_BaseDouble):  # type:ignore[valid-type,misc]
    """SAP HANA DOUBLE type.

    In SQLAlchemy 2.x, this extends DOUBLE.
    In SQLAlchemy 1.x, this extends FLOAT.
    """


class FLOAT(sqltypes.FLOAT):  # type:ignore[type-arg]
    """SAP HANA Float type."""


class BOOLEAN(sqltypes.BOOLEAN):
    """SAP HANA BOOLEAN type."""


class VARCHAR(sqltypes.VARCHAR):
    """SAP HANA VARCHAR type."""

    __visit_name__ = "VARCHAR"

    def __init__(self, length: int | None = None, collation: str | None = None) -> None:
        if length is not None and length > 5000:
            raise ValueError("VARCHAR does only support a length up to 5000 characters")
        super().__init__(length, collation)


class NVARCHAR(sqltypes.NVARCHAR):
    """SAP HANA NVARCHAR type."""


class ALPHANUM(sqltypes.String):
    """SAP HANA ALPHANUM type."""

    __visit_name__ = "ALPHANUM"

    def __init__(self, length: int | None = None, collation: str | None = None) -> None:
        if length is not None and length > 127:
            raise ValueError("Alphanum does only support a length up to 127 characters")
        super().__init__(length, collation)


class CHAR(sqltypes.CHAR):
    """SAP HANA CHAR type."""


class NCHAR(sqltypes.NCHAR):
    """SAP HANA NCHAR type."""


class VARBINARY(sqltypes.VARBINARY):
    """SAP HANA VARBINARY type."""


class BLOB(sqltypes.BLOB):
    """SAP HANA BLOB type."""


class CLOB(sqltypes.CLOB):
    """SAP HANA CLOB type."""


class NCLOB(sqltypes.UnicodeText):
    """SAP HANA NCLOB type."""

    __visit_name__ = "NCLOB"


class JSON(sqltypes.JSON):
    """SAP HANA JSON type."""


class REAL_VECTOR(TypeEngine[_RV], Generic[_RV]):
    """SAP HANA REAL_VECTOR type."""

    __visit_name__ = "REAL_VECTOR"

    def __init__(self, length: int | None = None) -> None:
        self.length = length


__all__ = [
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
    "REAL_VECTOR",
    "SECONDDATE",
    "SMALLDECIMAL",
    "SMALLINT",
    "TIME",
    "TIMESTAMP",
    "TINYINT",
    "VARBINARY",
    "VARCHAR",
]


if sqlalchemy.__version__ >= "2":
    # pylint: disable=unused-import
    from sqlalchemy_hana._uuid import Uuid  # noqa: F401

    __all__.append("Uuid")
