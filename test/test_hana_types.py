"""SAP HANA type testing."""

from __future__ import annotations

from unittest import mock

import pytest
from sqlalchemy import Boolean, inspect, testing
from sqlalchemy.testing.fixtures import TestBase
from sqlalchemy.testing.schema import Column, Table

from sqlalchemy_hana.types import SMALLDECIMAL, TINYINT


class HANATypeTest(TestBase):
    __backend__ = True

    @testing.provide_metadata
    def test_smalldecimal_insert_select(self):
        with testing.db.connect() as connection, connection.begin():
            table = Table(
                "t", self.metadata, Column("x", SMALLDECIMAL(asdecimal=False))
            )
            table.create(bind=connection)

            insert = table.insert().values(x=1.01)
            connection.execute(insert)

            select = table.select()
            for row in connection.execute(select):
                value = row[0]
                assert value == 1.01

    @testing.provide_metadata
    def test_smalldecimal_reflection(self):
        with testing.db.connect() as connection, connection.begin():
            table = Table("t", self.metadata, Column("x", SMALLDECIMAL))
            table.create(bind=connection)

            result = inspect(connection).get_columns("t")
            assert result == [
                {
                    "name": "x",
                    "default": None,
                    "nullable": True,
                    "comment": None,
                    "type": mock.ANY,
                }
            ]
            assert isinstance(result[0]["type"], SMALLDECIMAL)

    @testing.provide_metadata
    @pytest.mark.parametrize(
        "supports_native_boolean,type_", [(True, Boolean), (False, TINYINT)]
    )
    def test_native_boolean(self, supports_native_boolean, type_):
        with mock.patch.object(
            testing.db.engine.dialect,
            "supports_native_boolean",
            supports_native_boolean,
        ), testing.db.connect() as connection, connection.begin():
            table = Table("t", self.metadata, Column("x", Boolean))
            table.create(bind=connection)

            insert = table.insert().values(x=False)
            connection.execute(insert)

            row = connection.execute(table.select()).scalar()
            assert isinstance(row, bool)
            assert not row

            result = inspect(connection).get_columns("t")
            assert result == [
                {
                    "name": "x",
                    "default": None,
                    "nullable": True,
                    "comment": None,
                    "type": mock.ANY,
                }
            ]
            assert isinstance(result[0]["type"], type_)
