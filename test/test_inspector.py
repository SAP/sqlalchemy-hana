"""SAP HANA Inspector tests."""

from __future__ import annotations

from sqlalchemy import Integer, String, create_engine, inspect
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.testing import config, eq_, is_true
from sqlalchemy.testing.fixtures import TablesTest
from sqlalchemy.testing.schema import Column, Table

from sqlalchemy_hana.dialect import HANAInspector


class InspectorTest(TablesTest):

    @classmethod
    def define_tables(cls, metadata):
        Table(
            "tbl",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("desc", String(100)),
        )

    def test_get_table_oid(self, connection):
        connection_inspector = inspect(connection)

        is_true(isinstance(connection_inspector, HANAInspector))
        is_true(isinstance(connection_inspector.bind, Connection))

        table_oid1 = connection_inspector.get_table_oid(
            self.tables.tbl.name, self.tables.tbl.schema
        )
        is_true(isinstance(table_oid1, int))

        eng = create_engine(config.db.url)
        eng_inspector = inspect(eng)

        is_true(isinstance(eng_inspector, HANAInspector))
        is_true(isinstance(eng_inspector.bind, Engine))

        table_oid2 = eng_inspector.get_table_oid(
            self.tables.tbl.name, self.tables.tbl.schema
        )
        is_true(isinstance(table_oid2, int))

        eq_(table_oid1, table_oid2)
