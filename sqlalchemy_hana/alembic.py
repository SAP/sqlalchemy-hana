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

from sqlalchemy import schema
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import CreateSequence, DropSequence

from alembic.ddl.impl import DefaultImpl
from alembic.ddl.sqlite import SQLiteImpl
from alembic.ddl.base import (
    AddColumn,
    DropColumn,
    ColumnName,
    ColumnType,
    alter_table,
    format_column_name,
    format_table_name,
    format_type,
    format_server_default,
    ColumnNullable,
    ColumnDefault,
)


class HANAImpl(DefaultImpl):
    """Alembic implementation for SAP HANA."""

    __dialect__ = "hana"
    transactional_ddl = True

    def start_migrations(self):
        # Activate transactional DDL statements
        self.execute("SET TRANSACTION AUTOCOMMIT DDL OFF")


@compiles(AddColumn, "hana")
def visit_add_column(element, compiler, **kw):
    """Generate SQL statement to add column to existing table."""
    return "%s %s" % (
        alter_table(compiler, element.table_name, element.schema),
        "ADD (%s)" % compiler.get_column_specification(element.column, **kw),
    )


@compiles(DropColumn, "hana")
def visit_drop_column(element, compiler, **kw):
    """Generate SQL statement to remove column from existing table."""

    return "%s %s" % (
        alter_table(compiler, element.table_name, element.schema),
        "DROP (%s)" % format_column_name(compiler, element.column.name),
    )


@compiles(ColumnName, "hana")
def visit_rename_column(element, compiler):
    """Generate SQL statement to rename an existing column."""

    return "RENAME COLUMN %s.%s TO %s" % (
        format_table_name(compiler, element.table_name, element.schema),
        format_column_name(compiler, element.column_name),
        format_column_name(compiler, element.newname),
    )


@compiles(ColumnType, "hana")
def visit_column_type(element, compiler):
    """Generate SQL statement to adjust type of an existing column."""

    return "%s ALTER (%s %s)" % (
        alter_table(compiler, element.table_name, element.schema),
        format_column_name(compiler, element.column_name),
        format_type(compiler, element.type_),
    )


@compiles(ColumnNullable, "hana")
def visit_column_nullable(element, compiler):
    """Generate SQL statement to make a column nullable or not."""

    assert element.existing_type

    return "%s ALTER (%s %s %s)" % (
        alter_table(compiler, element.table_name, element.schema),
        format_column_name(compiler, element.column_name),
        format_type(compiler, element.existing_type),
        "NULL" if element.nullable else "NOT NULL",
    )


@compiles(ColumnDefault, "hana")
def visit_column_default(element, compiler):
    """Generate SQL statement to column default."""

    return "%s ALTER (%s %s DEFAULT %s)" % (
        alter_table(compiler, element.table_name, element.schema),
        format_column_name(compiler, element.column_name),
        format_type(compiler, element.existing_type),
        format_server_default(compiler, element.default)
        if element.default is not None
        else "NULL",
    )
