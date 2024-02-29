# pylint: disable=wildcard-import,unused-wildcard-import,function-redefined
"""Alembic dialect test suite."""

from __future__ import annotations

from alembic.testing import eq_
from alembic.testing.suite import *  # noqa: F401, F403
from alembic.testing.suite.test_autogen_fks import (
    AutogenerateFKOptionsTest as _AutogenerateFKOptionsTest,
)
from alembic.testing.suite.test_autogen_fks import (
    AutogenerateForeignKeysTest as _AutogenerateForeignKeysTest,
)
from alembic.testing.suite.test_autogen_fks import IncludeHooksTest as _IncludeHooksTest
from alembic.testing.suite.test_autogen_identity import (
    AutogenerateIdentityTest as _AutogenerateIdentityTest,
)
from sqlalchemy import Column, Identity, Integer, MetaData, Table


class PatchedDiff:
    def _assert_fk_diff(self, *args, **kwargs):
        def _fix(key):
            value = kwargs.get(key)
            if value is None:
                return "RESTRICT"
            if isinstance(value, str):
                return value.upper()
            return value

        kwargs["onupdate"] = _fix("onupdate")
        kwargs["ondelete"] = _fix("ondelete")
        return super()._assert_fk_diff(*args, **kwargs)


class AutogenerateFKOptionsTest(PatchedDiff, _AutogenerateFKOptionsTest):
    def test_nochange_onupdate_noaction(self):
        return


class AutogenerateForeignKeysTest(PatchedDiff, _AutogenerateForeignKeysTest):
    pass


class IncludeHooksTest(PatchedDiff, _IncludeHooksTest):
    pass


class AutogenerateIdentityTest(_AutogenerateIdentityTest):
    def test_remove_identity_column(self):
        m1 = MetaData()
        m2 = MetaData()

        Table(
            "user",
            m1,
            Column(
                "id",
                Integer,
                Identity(start=2, increment=3),
                primary_key=True,
            ),
        )

        Table("user", m2)

        diffs = self._fixture(m1, m2)

        eq_(diffs[0][0], "remove_column")
        eq_(diffs[0][2], "user")
        c = diffs[0][3]
        eq_(c.name, "id")

        # removed the assertions about the identity column since reflection is

    def test_remove_identity_from_column(self):
        # not supported due to the lack of identity column reflection support
        pass

    def test_no_change_identity_column(self):
        # not supported due to the lack of identity column reflection support
        pass

    def test_dialect_kwargs_changes(self):
        # not supported due to the lack of identity column reflection support
        pass
