"""SAP HANA SQL testing."""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    MetaData,
    Table,
    and_,
    false,
    func,
    literal,
    literal_column,
    not_,
    or_,
    select,
    true,
)
from sqlalchemy.sql.expression import column, table
from sqlalchemy.testing.assertions import AssertsCompiledSQL
from sqlalchemy.testing.fixtures import TestBase

from sqlalchemy_hana.dialect import HANAHDBCLIDialect


class SQLCompileTest(TestBase, AssertsCompiledSQL):
    __dialect__ = "hana"

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

        self.assert_compile(
            table1.select().with_for_update(of=table1),
            "SELECT mytable.myid, mytable.name, mytable.description "
            "FROM mytable FOR UPDATE OF mytable.myid, mytable.name, mytable.description",
        )

    def test_sql_unary_boolean(self) -> None:
        self.assert_compile(
            select(literal(1)).where(true()),
            "SELECT __[POSTCOMPILE_param_1] AS anon_1 FROM DUMMY WHERE true = TRUE",
        )

    def test_sql_unary_boolean_non_native(self) -> None:
        # With use_native_boolean=False, sql.true()/sql.false() render as
        # 1/0 (INT). Comparing INT to the boolean literals TRUE/FALSE raises
        # HANA error 266 (BOOLEAN type is not comparable with INT), so the
        # is_true/is_false unary wrappers must emit an INT compare instead.
        dialect = HANAHDBCLIDialect(use_native_boolean=False)

        self.assert_compile(
            select(literal_column("id")).where(false()),
            "SELECT id FROM DUMMY WHERE 0 = 1",
            dialect=dialect,
        )
        self.assert_compile(
            select(literal_column("id")).where(true()),
            "SELECT id FROM DUMMY WHERE 1 = 1",
            dialect=dialect,
        )
        # and_(false(), ...) is short-circuited by SQLAlchemy to just
        # false(); make sure that resulting predicate still renders as
        # a safe INT compare.
        self.assert_compile(
            select(literal_column("id")).where(
                and_(false(), literal_column("flag") == literal_column("1"))
            ),
            "SELECT id FROM DUMMY WHERE 0 = 1",
            dialect=dialect,
        )

    def test_sql_negated_or_predicate(self) -> None:
        # Negating a grouped boolean predicate (``~or_(...)``) must render
        # ``NOT (...)`` and not ``(...) = FALSE`` which SAP HANA rejects with
        # error 257 ("incorrect syntax near '='").
        table1 = table("mytable", column("url"))
        self.assert_compile(
            select(table1.c.url).where(~or_(table1.c.url.startswith("foo"))),
            "SELECT mytable.url FROM mytable WHERE NOT (mytable.url LIKE ? || '%')",
        )

    def test_sql_negated_and_predicate(self) -> None:
        table1 = table("mytable", column("url"))
        self.assert_compile(
            select(table1.c.url).where(~and_(table1.c.url.startswith("foo"))),
            "SELECT mytable.url FROM mytable WHERE NOT (mytable.url LIKE ? || '%')",
        )

    def test_sql_negated_grouping_predicate(self) -> None:
        table1 = table("mytable", column("url"))
        expected = (
            "SELECT mytable.url FROM mytable WHERE NOT "
            "((mytable.url LIKE ? || '%') OR (mytable.url LIKE ? || '%'))"
        )
        self.assert_compile(
            select(table1.c.url).where(
                not_(
                    or_(
                        table1.c.url.startswith("foo"),
                        table1.c.url.startswith("bar"),
                    )
                )
            ),
            expected,
        )

    def test_sql_negated_predicate_non_native(self) -> None:
        # The same must hold with use_native_boolean=False: ``(<predicate>) = 0``
        # is also rejected by HANA with error 257, so a negated predicate must
        # still render as ``NOT (...)``.
        dialect = HANAHDBCLIDialect(use_native_boolean=False)
        table1 = table("mytable", column("url"))
        self.assert_compile(
            select(table1.c.url).where(~or_(table1.c.url.startswith("foo"))),
            "SELECT mytable.url FROM mytable WHERE NOT (mytable.url LIKE ? || '%')",
            dialect=dialect,
        )

    def test_sql_negated_boolean_column(self) -> None:
        # A real boolean *column* is not implicitly boolean, so on SAP HANA it
        # must still be compared explicitly (``NOT flag`` / bare ``flag`` are
        # rejected by HANA). Native mode uses = TRUE/= FALSE.
        metadata_table = Table(
            "mytable",
            MetaData(),
            Column("id", Integer, primary_key=True),
            Column("flag", Boolean),
        )
        self.assert_compile(
            select(metadata_table.c.id).where(~metadata_table.c.flag),
            "SELECT mytable.id FROM mytable WHERE mytable.flag = FALSE",
        )
        self.assert_compile(
            select(metadata_table.c.id).where(metadata_table.c.flag),
            "SELECT mytable.id FROM mytable WHERE mytable.flag = TRUE",
        )

    def test_sql_negated_boolean_column_non_native(self) -> None:
        # With use_native_boolean=False a boolean column stores as integer, so
        # it must be compared with = 0/= 1 (not NOT/bare column).
        dialect = HANAHDBCLIDialect(use_native_boolean=False)
        metadata_table = Table(
            "mytable",
            MetaData(),
            Column("id", Integer, primary_key=True),
            Column("flag", Boolean),
        )
        self.assert_compile(
            select(metadata_table.c.id).where(~metadata_table.c.flag),
            "SELECT mytable.id FROM mytable WHERE mytable.flag = 0",
            dialect=dialect,
        )
        self.assert_compile(
            select(metadata_table.c.id).where(metadata_table.c.flag),
            "SELECT mytable.id FROM mytable WHERE mytable.flag = 1",
            dialect=dialect,
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

    def test_sql_with_statement_hint_single(self) -> None:
        table1 = table("mytable", column("myid"))
        self.assert_compile(
            table1.select().with_statement_hint("NO_CS_JOIN"),
            "SELECT mytable.myid FROM mytable WITH HINT(NO_CS_JOIN)",
        )

    def test_sql_with_statement_hint_multiple(self) -> None:
        table1 = table("mytable", column("myid"))
        self.assert_compile(
            table1.select()
            .with_statement_hint("NO_CS_JOIN")
            .with_statement_hint("HASH_JOIN"),
            "SELECT mytable.myid FROM mytable WITH HINT(NO_CS_JOIN, HASH_JOIN)",
        )

    def test_sql_with_statement_hint_dialect_filter(self) -> None:
        table1 = table("mytable", column("myid"))
        # hint with dialect_name="*" should be included
        self.assert_compile(
            table1.select().with_statement_hint("NO_CS_JOIN", dialect_name="*"),
            "SELECT mytable.myid FROM mytable WITH HINT(NO_CS_JOIN)",
        )
        # hint targeted at another dialect should not appear
        self.assert_compile(
            table1.select().with_statement_hint(
                "NO_CS_JOIN", dialect_name="postgresql"
            ),
            "SELECT mytable.myid FROM mytable",
        )
