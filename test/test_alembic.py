# pylint: disable=deprecated-method,invalid-name
"""Custom tests for alembic."""

from __future__ import annotations

import sqlalchemy
from alembic import op
from alembic.migration import MigrationContext
from alembic.testing.assertions import _dialect_mods
from alembic.testing.fixtures import op_fixture
from sqlalchemy import Column
from sqlalchemy.testing import config
from sqlalchemy.testing.fixtures import TestBase

from sqlalchemy_hana.alembic import HANAImpl
from sqlalchemy_hana.dialect import HANAHDBCLIDialect


class AlembicHANATest(TestBase):
    def test_configure_hana_migration_context(self):
        context = MigrationContext.configure(url="hana://localhost:30015")
        assert isinstance(context.dialect, HANAHDBCLIDialect)
        assert isinstance(context.impl, HANAImpl)


class AlembicHANAOperationTest(TestBase):
    def setUp(self):
        class FakeModule:
            def dialect(self):
                return config.db.dialect

        _dialect_mods["hana"] = FakeModule()

    def tearDown(self):
        del _dialect_mods["hana"]

    def test_add_column(self):
        context = op_fixture("hana")
        op.add_column("some_table", Column("column_a", sqlalchemy.INTEGER))
        context.assert_("ALTER TABLE some_table ADD (column_a INTEGER)")

    def test_add_column_with_server_default(self):
        context = op_fixture("hana")
        op.add_column(
            "some_table",
            Column(
                "column_a", sqlalchemy.TIMESTAMP, server_default=sqlalchemy.func.now()
            ),
        )
        context.assert_(
            "ALTER TABLE some_table ADD (column_a TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )

    def test_drop_column(self):
        context = op_fixture("hana")
        op.drop_column("some_table", "column_a")
        context.assert_("ALTER TABLE some_table DROP (column_a)")

    def test_alter_column_type(self):
        context = op_fixture("hana")
        op.alter_column("some_table", "column_a", type_=sqlalchemy.VARCHAR(500))
        context.assert_("ALTER TABLE some_table ALTER (column_a VARCHAR(500))")

    def test_alter_column_nullable(self):
        context = op_fixture("hana")
        op.alter_column(
            "some_table",
            "column_a",
            existing_type=sqlalchemy.VARCHAR(500),
            nullable=True,
        )
        context.assert_("ALTER TABLE some_table ALTER (column_a VARCHAR(500) NULL)")

    def test_alter_column_not_nullable(self):
        context = op_fixture("hana")
        op.alter_column(
            "some_table",
            "column_a",
            existing_type=sqlalchemy.VARCHAR(500),
            nullable=False,
        )
        context.assert_("ALTER TABLE some_table ALTER (column_a VARCHAR(500) NOT NULL)")

    def test_alter_column_new_server_default(self):
        context = op_fixture("hana")
        op.alter_column(
            "some_table",
            "column_a",
            existing_type=sqlalchemy.VARCHAR(500),
            server_default=sqlalchemy.func.now(),
        )
        context.assert_(
            "ALTER TABLE some_table ALTER (column_a VARCHAR(500) DEFAULT CURRENT_TIMESTAMP)"
        )

    def test_rename_simple_column(self):
        context = op_fixture("hana")
        op.alter_column("some_table", "column_a", new_column_name="column_b")
        context.assert_("RENAME COLUMN some_table.column_a TO column_b")

    def test_rename_mix_case_column(self):
        context = op_fixture("hana")
        op.alter_column("strange Table nAme", "colume A 1", new_column_name="column_a")
        context.assert_(
            """RENAME COLUMN "strange Table nAme"."colume A 1" TO column_a"""
        )

    def test_rename_table(self):
        context = op_fixture("hana")
        op.rename_table("old_table", "new_table")
        context.assert_("RENAME TABLE old_table TO new_table")

    def test_create_check_constraint(self):
        context = op_fixture("hana")
        op.create_check_constraint(
            "ck_constraint_name", "some_table", Column("age") > 0
        )
        context.assert_(
            """ALTER TABLE some_table ADD CONSTRAINT ck_constraint_name CHECK (age > 0)"""
        )

    def test_drop_primary_key(self):
        context = op_fixture("hana")
        op.drop_constraint("pk", "some_table", type_="primary")
        context.assert_("ALTER TABLE some_table DROP PRIMARY KEY")
