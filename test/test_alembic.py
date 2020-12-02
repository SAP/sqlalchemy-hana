# Copyright 2020 SAP SE.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http: //www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import sqlalchemy
from sqlalchemy import testing
from sqlalchemy.testing.suite import fixtures

from alembic import op
from alembic.migration import MigrationContext
from alembic.testing.fixtures import op_fixture
from alembic.testing.assertions import _dialect_mods

class AlembicHANATest(fixtures.TestBase):

    def test_configure_hana_migration_context(self):
        context = MigrationContext.configure(
            url='hana://localhost:30015'
        )

        from sqlalchemy_hana.dialect import HANABaseDialect
        from sqlalchemy_hana.alembic import HANAImpl

        assert isinstance(context.dialect, HANABaseDialect)
        assert isinstance(context.impl, HANAImpl)


class AlembicHANAOperationTest(fixtures.TestBase):

    def setUp(self):
        class FakeModule(object):
            def dialect(self):
                return testing.db.dialect

        _dialect_mods['hana'] = FakeModule()

    def tearDown(self):
        del _dialect_mods['hana']

    def test_add_column(self):
        context = op_fixture("hana")
        op.add_column('some_table',
            sqlalchemy.Column('column_a', sqlalchemy.INTEGER)
        )
        context.assert_("ALTER TABLE some_table ADD (column_a INTEGER)")

    def test_add_column_with_server_default(self):
        context = op_fixture("hana")
        op.add_column('some_table',
            sqlalchemy.Column('column_a', sqlalchemy.TIMESTAMP, server_default=sqlalchemy.func.now())
        )
        context.assert_("ALTER TABLE some_table ADD (column_a TIMESTAMP DEFAULT now())")

    def test_drop_column(self):
        context = op_fixture("hana")
        op.drop_column('some_table', 'column_a')
        context.assert_("ALTER TABLE some_table DROP (column_a)")

    def test_alter_column_type(self):
        context = op_fixture("hana")
        op.alter_column('some_table', 'column_a', type_=sqlalchemy.VARCHAR(500))
        context.assert_("ALTER TABLE some_table ALTER (column_a VARCHAR(500))")

    def test_alter_column_nullable(self):
        context = op_fixture("hana")
        op.alter_column('some_table', 'column_a', existing_type=sqlalchemy.VARCHAR(500), nullable=True)
        context.assert_("ALTER TABLE some_table ALTER (column_a VARCHAR(500) NULL)")

    def test_alter_column_not_nullable(self):
        context = op_fixture("hana")
        op.alter_column('some_table', 'column_a', existing_type=sqlalchemy.VARCHAR(500), nullable=False)
        context.assert_("ALTER TABLE some_table ALTER (column_a VARCHAR(500) NOT NULL)")

    def test_alter_column_new_server_default(self):
        context = op_fixture("hana")
        op.alter_column('some_table', 'column_a', existing_type=sqlalchemy.VARCHAR(500), server_default=sqlalchemy.func.now())
        context.assert_("ALTER TABLE some_table ALTER (column_a VARCHAR(500) DEFAULT now())")

    def test_rename_simple_column(self):
        context = op_fixture("hana")
        op.alter_column(
            "some_table",
            "column_a",
            new_column_name="column_b"
        )
        context.assert_("RENAME COLUMN some_table.column_a TO column_b")

    def test_rename_mix_case_column(self):
        context = op_fixture("hana")
        op.alter_column(
            "strange Table nAme",
            "colume A 1",
            new_column_name="column_a"
        )
        context.assert_("""RENAME COLUMN "strange Table nAme"."colume A 1" TO column_a""")

    def test_create_check_constraint(self):
        context = op_fixture("hana")
        op.create_check_constraint(
            "ck_constraint_name",
            "some_table",
            sqlalchemy.column("age") > 0
        )
        context.assert_("""ALTER TABLE some_table ADD CONSTRAINT ck_constraint_name CHECK (age > 0)""")
