"""SAP HANA types."""

from __future__ import annotations

from datetime import date, datetime, time
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Literal, cast

from sqlalchemy import types as sqltypes
from sqlalchemy.engine import Dialect

if TYPE_CHECKING:
    from sqlalchemy_hana.dialect import HANAHDBCLIDialect


class TINYINT(sqltypes.Integer):
    __visit_name__ = "TINYINT"


class DOUBLE(sqltypes.Float):  # type:ignore[type-arg]
    __visit_name__ = "DOUBLE"


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


class BOOLEAN(sqltypes.Boolean):
    def get_dbapi_type(self, dbapi: ModuleType) -> Any | None:
        return dbapi.NUMBER


class DATE(sqltypes.Date):
    def literal_processor(self, dialect: Dialect) -> Callable[[Any], str]:
        self.bind_processor(dialect)

        def process(value: date) -> str:
            return f"to_date('{value}')"

        return process


class TIME(sqltypes.Time):
    def literal_processor(self, dialect: Dialect) -> Callable[[Any], str]:
        self.bind_processor(dialect)

        def process(value: time) -> str:
            return f"to_time('{value}')"

        return process


class TIMESTAMP(sqltypes.DateTime):
    def literal_processor(self, dialect: Dialect) -> Callable[[Any], str]:
        self.bind_processor(dialect)

        def process(value: datetime) -> str:
            return f"to_timestamp('{value}')"

        return process


class _LOBMixin:
    def result_processor(
        self, dialect: Dialect, coltype: object
    ) -> Callable[[Any], Any] | None:
        dialect = cast("HANAHDBCLIDialect", dialect)

        def process(value: Any) -> Any | None:
            if value is None:
                return None
            if isinstance(value, str):
                return value
            if isinstance(value, memoryview):
                return value.obj
            if hasattr(value, "read"):
                return value.read()
            raise NotImplementedError

        return process


class HanaText(_LOBMixin, sqltypes.Text):
    def get_dbapi_type(self, dbapi: ModuleType) -> Any | None:
        return dbapi.CLOB


class HanaUnicodeText(_LOBMixin, sqltypes.UnicodeText):
    def get_dbapi_type(self, dbapi: ModuleType) -> Any | None:
        return dbapi.NCLOB

    def result_processor(
        self, dialect: Dialect, coltype: object
    ) -> Callable[[Any], str] | None:
        lob_processor = _LOBMixin.result_processor(self, dialect, coltype)
        if lob_processor is None:
            return None

        string_processor = sqltypes.UnicodeText.result_processor(self, dialect, coltype)
        if string_processor is None:
            return lob_processor

        def process(value: Any) -> str:
            return string_processor(lob_processor(value))

        return process


class HanaBinary(_LOBMixin, sqltypes.LargeBinary):
    def get_dbapi_type(self, dbapi: ModuleType) -> Any | None:
        return dbapi.BLOB

    def bind_processor(self, dialect: Dialect) -> None:
        return None


class NCLOB(sqltypes.Text):
    __visit_name__ = "NCLOB"
