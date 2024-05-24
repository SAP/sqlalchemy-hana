# pylint: disable=wildcard-import,unused-wildcard-import,function-redefined,arguments-differ
# pylint: disable=redefined-outer-name
"""SQLAlchemy dialect test suite."""

from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy import (
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    inspect,
    testing,
)
from sqlalchemy.exc import DBAPIError
from sqlalchemy.testing.assertions import assert_raises, eq_
from sqlalchemy.testing.provision import temp_table_keyword_args
from sqlalchemy.testing.schema import Column, Table
from sqlalchemy.testing.suite import *  # noqa: F401, F403
from sqlalchemy.testing.suite.test_cte import CTETest as _CTETest
from sqlalchemy.testing.suite.test_reflection import (
    ComponentReflectionTest as _ComponentReflectionTest,
)
from sqlalchemy.testing.suite.test_reflection import (
    ComponentReflectionTestExtra as _ComponentReflectionTestExtra,
)
from sqlalchemy.testing.suite.test_reflection import (
    IdentityReflectionTest as _IdentityReflectionTest,
)
from sqlalchemy.testing.suite.test_select import (
    IdentityColumnTest as _IdentityColumnTest,
)
from sqlalchemy.testing.suite.test_types import JSONTest as _JSONTest

# Import dialect test suite provided by SQLAlchemy into SQLAlchemy-HANA test collection.
# Please don't add other tests in this file. Only adjust or overview SQLAlchemy tests
# for compatibility with SAP HANA.


@temp_table_keyword_args.for_db("*")
def _temp_table_keyword_args(*args: Any, **kwargs: Any) -> dict[str, list[str]]:
    return {
        "prefixes": ["GLOBAL TEMPORARY"],
    }


class ComponentReflectionTestExtra(_ComponentReflectionTestExtra):
    @testing.combinations(
        ("CASCADE", None),
        (None, "SET NULL"),
        (None, "RESTRICT"),
        (None, "RESTRICT"),
        argnames="ondelete,onupdate",
    )
    def test_get_foreign_key_options(self, connection, metadata, ondelete, onupdate):
        options = {}
        if ondelete:
            options["ondelete"] = ondelete
        if onupdate:
            options["onupdate"] = onupdate

        options.setdefault("ondelete", "RESTRICT")
        options.setdefault("onupdate", "RESTRICT")

        Table(
            "x",
            metadata,
            Column("id", Integer, primary_key=True),
            test_needs_fk=True,
        )

        Table(
            "table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("x_id", Integer, ForeignKey("x.id", name="xid")),
            Column("test", String(10)),
            test_needs_fk=True,
        )

        Table(
            "user",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50), nullable=False),
            Column("tid", Integer),
            ForeignKeyConstraint(["tid"], ["table.id"], name="myfk", **options),
            test_needs_fk=True,
        )

        metadata.create_all(connection)

        insp = inspect(connection)

        # test 'options' is always present for a backend
        # that can reflect these, since alembic looks for this
        opts = insp.get_foreign_keys("table")[0]["options"]

        eq_(
            {k: opts[k] for k in opts if opts[k]},
            {"onupdate": "RESTRICT", "ondelete": "RESTRICT"},
        )

        opts = insp.get_foreign_keys("user")[0]["options"]
        eq_(opts, options)


class ComponentReflectionTest(_ComponentReflectionTest):
    def _check_table_dict(self, result, exp, req_keys=None, make_lists=False):
        def _normalize(data):
            for entry in data.values():
                if isinstance(entry, list):
                    for subentry in entry:
                        if "sqltext" not in subentry:
                            continue
                        sqltext = subentry["sqltext"]
                        # ignore casing
                        sqltext = sqltext.lower()
                        # removes spaces because they are not consistent
                        sqltext = sqltext.replace(" ", "")
                        # remove quotes because they are not consistent
                        sqltext = sqltext.replace('"', "")
                        # remove a potential leading (
                        if sqltext.startswith("("):
                            sqltext = sqltext[1:]
                        # remove a potential closing )
                        if sqltext.endswith(")"):
                            sqltext = sqltext[:-1]
                        subentry["sqltext"] = sqltext

        _normalize(result)
        _normalize(exp)
        return super()._check_table_dict(result, exp, req_keys, make_lists)


class CTETest(_CTETest):
    def test_select_recursive_round_trip(self, connection):
        pytest.skip("Recursive CTEs are not supported by SAP HANA")

    def test_insert_from_select_round_trip(self, connection):
        pytest.skip("Insert CTEs are not supported by SAP HANA")


class IdentityReflectionTest(_IdentityReflectionTest):
    def test_reflect_identity(self, connection):
        pytest.skip("Identity column reflection is not supported")

    def test_reflect_identity_schema(self, connection):
        pytest.skip("Identity column reflection is not supported")


class IdentityColumnTest(_IdentityColumnTest):
    def test_insert_always_error(self, connection):
        def fn():
            connection.execute(
                self.tables.tbl_a.insert(),
                [{"id": 200, "desc": "a"}],
            )

        assert_raises((DBAPIError,), fn)


class JSONTest(_JSONTest):
    @classmethod
    def define_tables(cls, metadata):
        Table(
            "data_table",
            metadata,
            Column("id", Integer, autoincrement=True, primary_key=True),
            Column("name", String(30), nullable=False),
            Column("data", cls.datatype, nullable=False),
            Column("nulldata", cls.datatype(none_as_null=True)),
        )

    def test_index_typed_access(self):
        pytest.skip("Index typed access is not supported")

    def test_index_typed_comparison(self):
        pytest.skip("Index typed access is not supported")

    def test_path_typed_comparison(self):
        pytest.skip("Path typed access is not supported")
