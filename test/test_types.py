# pylint: disable=attribute-defined-outside-init
"""Tests for sqlalchemy_hana.types."""

from __future__ import annotations

import datetime
import decimal
import random
from unittest import mock
from uuid import UUID

import pytest
import sqlalchemy
import sqlalchemy.testing.suite.test_types
from sqlalchemy import inspect, testing, types
from sqlalchemy.schema import CreateTable
from sqlalchemy.testing.fixtures import TablesTest, TestBase
from sqlalchemy.testing.schema import Column, Table
from sqlalchemy.testing.suite.test_types import _DateFixture

from sqlalchemy_hana import types as hana_types


class SecondDateTest(_DateFixture, TablesTest):
    __backend__ = True
    datatype = hana_types.SECONDDATE
    data = datetime.datetime(2012, 10, 15, 12, 57, 18, 12345)
    compare = datetime.datetime(2012, 10, 15, 12, 57, 18)


class _TypeBaseTest(TablesTest):
    compare = None

    @classmethod
    def define_tables(cls, metadata):
        sqlalchemy.Table(
            "test_type",
            metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column("data", cls.column_type),
        )

    @property
    def reflected_column_type(self):
        return self.column_type

    def test_round_trip(self, connection):
        test_type = self.tables.test_type

        connection.execute(test_type.insert(), {"id": 1, "data": self.data})

        row = connection.execute(sqlalchemy.select(test_type.c.data)).first()

        compare = self.compare or self.data
        assert row == (compare,)
        assert isinstance(row[0], type(compare))

    def test_reflection(self, connection):
        columns = sqlalchemy.inspect(connection).get_columns("test_type")
        assert isinstance(columns[1]["type"], self.reflected_column_type.__class__)
        assert repr(columns[1]["type"]) == repr(self.reflected_column_type)


class _IntegerBaseTest(_TypeBaseTest):
    column_type = None

    def test_round_trip(self, connection):
        self.data = random.randint(self.min_value, self.max_value)
        super().test_round_trip(connection)

    def test_underflow_int(self, connection):
        test_type = self.tables.test_type

        with pytest.raises(sqlalchemy.exc.DBAPIError):
            connection.execute(
                test_type.insert(), {"id": 1, "data": self.min_value - 1}
            )

    def test_overflow_int(self, connection):
        test_type = self.tables.test_type

        with pytest.raises(sqlalchemy.exc.DBAPIError):
            connection.execute(
                test_type.insert(), {"id": 1, "data": self.max_value + 1}
            )


class TinyIntTest(_IntegerBaseTest):
    column_type = hana_types.TINYINT()
    min_value = 0
    max_value = 255


class SmallIntTest(_IntegerBaseTest):
    column_type = hana_types.SMALLINT()
    min_value = -32768
    max_value = 32767


class IntegerTest(_IntegerBaseTest):
    column_type = hana_types.INTEGER()
    min_value = -2147483648
    max_value = 2147483647


class BigIntTest(_IntegerBaseTest):
    column_type = hana_types.BIGINT()
    min_value = -9_223_372_036_854_775_808
    max_value = 9_223_372_036_854_775_807


class SmallDecimalTest(_TypeBaseTest):
    column_type = hana_types.SMALLDECIMAL()
    data = decimal.Decimal("3.14")


class DecimalTest(_TypeBaseTest):
    column_type = hana_types.DECIMAL(5, 4)
    data = decimal.Decimal("3.141592")
    compare = decimal.Decimal("3.1415")


class RealTest(_TypeBaseTest):
    column_type = hana_types.REAL()
    data = 3.141592
    compare = 3.141592025756836


class DoubleTest(_TypeBaseTest):
    column_type = hana_types.DOUBLE()
    data = 3.141592


class BooleanTest(_TypeBaseTest):
    column_type = hana_types.BOOLEAN()
    data = True

    @testing.provide_metadata
    @pytest.mark.parametrize(
        "supports_native_boolean,type_",
        [(True, hana_types.BOOLEAN), (False, hana_types.TINYINT)],
    )
    def test_native_boolean(self, supports_native_boolean, type_):
        with (
            mock.patch.object(
                testing.db.engine.dialect,
                "supports_native_boolean",
                supports_native_boolean,
            ),
            testing.db.connect() as connection,
            connection.begin(),
        ):
            table = Table("t", self.metadata, Column("x", types.Boolean))
            table.create(bind=connection)

            insert = table.insert().values(x=False)
            connection.execute(insert)

            row = connection.execute(table.select()).scalar()
            assert isinstance(row, bool)
            assert not row

            result = inspect(connection).get_columns("t")
            assert isinstance(result[0]["type"], type_)


class VarcharTest(_TypeBaseTest):
    column_type = hana_types.VARCHAR(length=15)
    data = "Some text"

    @property
    def reflected_column_type(self):
        return hana_types.NVARCHAR(length=15)


class NVarcharTest(_TypeBaseTest):
    column_type = hana_types.NVARCHAR(length=15)
    data = "Some text"


class CharTest(_TypeBaseTest):
    column_type = hana_types.CHAR(length=60)
    data = "Some data for a HANA short text"

    @property
    def reflected_column_type(self):
        return hana_types.NCHAR(length=60)


class NCharTest(_TypeBaseTest):
    column_type = hana_types.NCHAR(length=60)
    data = "Some data for a HANA short text"


class VarBinaryTest(_TypeBaseTest):
    column_type = hana_types.VARBINARY(length=60)
    data = b"Some binary for a HANA VARBINARY"


class BLOBTest(_TypeBaseTest):
    column_type = hana_types.BLOB()
    data = b"some binary data"


class CLOBTest(_TypeBaseTest):
    column_type = hana_types.CLOB()
    data = "some test text"

    @property
    def reflected_column_type(self):
        return hana_types.NCLOB()


class NCLOBTest(_TypeBaseTest):
    column_type = hana_types.NCLOB()
    data = "some test text"


class JSONTest(_TypeBaseTest):
    column_type = hana_types.JSON()
    data = {"a": 1, "b": "2", "c": None}

    @property
    def reflected_column_type(self):
        return hana_types.NCLOB()


class AlphanumTest(TestBase):
    # no real test possible because ALPHANUM is not supported in SAP HANA Cloud

    def test_compile(self, connection, metadata) -> None:
        mytab = Table("mytab", metadata, Column("mycol", hana_types.ALPHANUM(10)))
        assert (
            str(CreateTable(mytab).compile(connection))
            == "\nCREATE TABLE mytab (\n\tmycol ALPHANUM(10)\n)\n\n"
        )


class RealVectorTest(_TypeBaseTest):
    column_type = hana_types.REAL_VECTOR()
    data = [1, 2, 3]

    @property
    def reflected_column_type(self):
        return hana_types.REAL_VECTOR()

    @testing.provide_metadata
    def test_reflection_with_length(self):
        with testing.db.connect() as connection, connection.begin():
            table = Table(
                "t",
                self.metadata,
                Column("vec1", hana_types.REAL_VECTOR(length=10)),
                Column("vec2", hana_types.REAL_VECTOR()),
            )
            table.create(bind=connection)

            columns = sqlalchemy.inspect(connection).get_columns("t")
            assert columns[0]["type"].length == 10
            assert columns[1]["type"].length is None


if sqlalchemy.__version__ >= "2":

    class StringUUIDAsStringTest(_TypeBaseTest):
        column_type = hana_types.Uuid(as_uuid=False)
        data = "9f01b2fb-bf0d-4b46-873c-15d0976b4100"

        @property
        def reflected_column_type(self):
            return hana_types.NVARCHAR(length=32)

    class StringUUIDAsUUIDTest(_TypeBaseTest):
        column_type = hana_types.Uuid(as_uuid=True)
        data = UUID("9f01b2fb-bf0d-4b46-873c-15d0976b4100")

        @property
        def reflected_column_type(self):
            return hana_types.NVARCHAR(length=32)

    class BinaryUUIDAsStringTest(_TypeBaseTest):
        column_type = hana_types.Uuid(as_uuid=False, as_varbinary=True)
        data = "9f01b2fb-bf0d-4b46-873c-15d0976b4100"

        @property
        def reflected_column_type(self):
            return hana_types.VARBINARY(length=16)

    class BinaryUUIDAsUUIDTest(_TypeBaseTest):
        column_type = hana_types.Uuid(as_uuid=True, as_varbinary=True)
        data = UUID("9f01b2fb-bf0d-4b46-873c-15d0976b4100")

        @property
        def reflected_column_type(self):
            return hana_types.VARBINARY(length=16)
