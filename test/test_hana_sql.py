"""SAP HANA SQL testing."""

from __future__ import annotations

import sqlalchemy.testing
from sqlalchemy.sql.expression import column, table


class HANACompileTest(
    sqlalchemy.testing.fixtures.TestBase, sqlalchemy.testing.AssertsCompiledSQL
):
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
            table1.select().with_for_update(skip_locked=True),
            "SELECT mytable.myid, mytable.name, mytable.description "
            "FROM mytable FOR UPDATE IGNORE LOCKED",
        )
