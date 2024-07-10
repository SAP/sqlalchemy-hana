"""SAP HANA SQL testing."""

from __future__ import annotations

from sqlalchemy import func, literal, select, true
from sqlalchemy.sql.expression import column, table
from sqlalchemy.testing.assertions import AssertsCompiledSQL
from sqlalchemy.testing.fixtures import TestBase


class SQLCompileTest(TestBase, AssertsCompiledSQL):
    def test_sql_with_for_update(self) -> None:
        table1 = table("mytable", column("myid"), column("name"), column("description"))

        self.assert_compile(
            table1.select().with_for_update(),
            "SELECT mytable.myid, mytable.name, mytable.description "
            "FROM mytable FOR UPDATE",
        )

        self.assert_compile(
            table1.select().with_for_update(nowait=True),
            "SELECT mytable.myid, mytable.name, mytable.description "
            "FROM mytable FOR UPDATE NOWAIT",
        )

        self.assert_compile(
            table1.select().with_for_update(read=True),
            "SELECT mytable.myid, mytable.name, mytable.description "
            "FROM mytable FOR SHARE LOCK",
        )

        self.assert_compile(
            table1.select().with_for_update(read=True, skip_locked=True),
            "SELECT mytable.myid, mytable.name, mytable.description "
            "FROM mytable FOR SHARE LOCK IGNORE LOCKED",
        )

        self.assert_compile(
            table1.select().with_for_update(skip_locked=True),
            "SELECT mytable.myid, mytable.name, mytable.description "
            "FROM mytable FOR UPDATE IGNORE LOCKED",
        )

    def test_sql_unary_boolean(self) -> None:
        self.assert_compile(
            select(literal(1)).where(true()),
            "SELECT __[POSTCOMPILE_param_1] AS anon_1 FROM DUMMY WHERE true = TRUE",
        )

    def test_sql_offset_without_limit(self) -> None:
        self.assert_compile(
            select(literal(1)).offset(100),
            "SELECT __[POSTCOMPILE_param_1] AS anon_1 FROM DUMMY LIMIT 2147384648 OFFSET ?",
        )

    def test_sql_now_function(self) -> None:
        self.assert_compile(
            select(func.now()), "SELECT CURRENT_TIMESTAMP AS now_1 FROM DUMMY"
        )
