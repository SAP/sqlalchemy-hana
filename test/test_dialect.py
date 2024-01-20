"""SAP HANA Dialect testing."""

from __future__ import annotations

from unittest import TestCase
from unittest.mock import Mock, MagicMock

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, ResultProxy
from sqlalchemy.testing.fixtures import TestBase
from sqlalchemy_hana.dialect import HANABaseDialect

DEFAULT_ISOLATION_LEVEL = "READ COMMITTED"
NON_DEFAULT_ISOLATION_LEVEL = "SERIALIZABLE"


class DialectTest(TestCase):
    def test_get_columns(self) -> None:
        # COLUMN_NAME, DATA_TYPE_NAME, DEFAULT_VALUE, IS_NULLABLE, LENGTH, SCALE, COMMENTS
        rows = [
            ["ID", "BIGINT", None, "FALSE", None, None, None],
            ["NAME", "NVARCHAR", None, "FALSE", 255, None, None],
            ["FIRST_NAME", "NVARCHAR", None, "FALSE", 255, None, None],
            ["GENDER", "NVARCHAR", "M", "FALSE", 1, None, None],
            ["BIRTHDATE", "DATE", None, "TRUE", None, None, None],
        ]
        connection = MagicMock(spec=Connection)
        result = MagicMock(spec=ResultProxy)
        result.fetchall.return_value = rows
        connection.execute.side_effect = lambda sql: result
        engine = create_engine("hana://user:pass@localhost:3005/HR")

        assert isinstance(engine.dialect, HANABaseDialect)

        actual = engine.dialect.get_columns(connection=connection, table_name="EMPLOYEES", schema="HR")

        assert actual is not None
        assert len(actual) == 5
        assert {'comment': None, 'default': None, 'name': 'id', 'nullable': False, 'type': sqlalchemy.sql.sqltypes.BIGINT} in actual
        assert {'comment': None, 'default': None, 'name': 'name', 'nullable': False, 'type': sqlalchemy.sql.sqltypes.NVARCHAR} in actual
        assert {'comment': None, 'default': None, 'name': 'first_name', 'nullable': False, 'type': sqlalchemy.sql.sqltypes.NVARCHAR} in actual
        assert {'comment': None, 'default': 'M', 'name': 'gender', 'nullable': False, 'type': sqlalchemy.sql.sqltypes.NVARCHAR} in actual
        assert {'comment': None, 'default': None, 'name': 'birthdate', 'nullable': True, 'type': sqlalchemy.sql.sqltypes.DATE} in actual

    def test_get_columns_when_normalize_column_name_disabled(self) -> None:
        # COLUMN_NAME, DATA_TYPE_NAME, DEFAULT_VALUE, IS_NULLABLE, LENGTH, SCALE, COMMENTS
        rows = [
            ["ID", "BIGINT", None, "FALSE", None, None, None],
            ["NAME", "NVARCHAR", None, "FALSE", 255, None, None],
            ["FIRST_NAME", "NVARCHAR", None, "FALSE", 255, None, None],
            ["GENDER", "NVARCHAR", "M", "FALSE", 1, None, None],
            ["BIRTHDATE", "DATE", None, "TRUE", None, None, None],
        ]
        connection = MagicMock(spec=Connection)
        result = MagicMock(spec=ResultProxy)
        result.fetchall.return_value = rows
        connection.execute.side_effect = lambda sql: result
        engine = create_engine("hana://user:pass@localhost:3005/HR", normalize_column_name=False)

        assert isinstance(engine.dialect, HANABaseDialect)

        actual = engine.dialect.get_columns(connection=connection, table_name="EMPLOYEES", schema="HR")

        assert actual is not None
        assert len(actual) == 5
        assert {'comment': None, 'default': None, 'name': 'ID', 'nullable': False, 'type': sqlalchemy.sql.sqltypes.BIGINT} in actual
        assert {'comment': None, 'default': None, 'name': 'NAME', 'nullable': False, 'type': sqlalchemy.sql.sqltypes.NVARCHAR} in actual
        assert {'comment': None, 'default': None, 'name': 'FIRST_NAME', 'nullable': False, 'type': sqlalchemy.sql.sqltypes.NVARCHAR} in actual
        assert {'comment': None, 'default': 'M', 'name': 'GENDER', 'nullable': False, 'type': sqlalchemy.sql.sqltypes.NVARCHAR} in actual
        assert {'comment': None, 'default': None, 'name': 'BIRTHDATE', 'nullable': True, 'type': sqlalchemy.sql.sqltypes.DATE} in actual
