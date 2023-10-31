"""SAP HANA types."""

from __future__ import annotations

from datetime import date, datetime, time
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, cast

from sqlalchemy import Dialect
from sqlalchemy import types as sqltypes

if TYPE_CHECKING:
    from sqlalchemy_hana.dialect import HANABaseDialect


class TINYINT(sqltypes.Integer):
    __visit_name__ = "TINYINT"


class DOUBLE(sqltypes.Float[float]):
    __visit_name__ = "DOUBLE"


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
        dialect = cast("HANABaseDialect", dialect)
        if not dialect.auto_convert_lobs:
            # Disable processor and return raw DBAPI LOB type
            return None

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
