"""SQL select tests."""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.testing.assertions import eq_
from sqlalchemy.testing.fixtures import TablesTest
from sqlalchemy.testing.schema import Column, Table


class SelectTest(TablesTest):

    @classmethod
    def define_tables(cls, metadata):
        Table(
            "tbl",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("desc", String(100)),
        )

    def test_autoincrement(self, connection):
        res = connection.execute(self.tables.tbl.insert(), {"desc": "row"})
        res = connection.execute(self.tables.tbl.select()).first()
        eq_(res, (1, "row"))
