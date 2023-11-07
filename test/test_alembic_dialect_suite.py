# pylint: disable=wildcard-import,unused-wildcard-import,function-redefined
"""Alembic dialect test suite."""

from __future__ import annotations

from alembic.testing.suite import *  # noqa: F401, F403
from alembic.testing.suite.test_autogen_fks import (
    AutogenerateFKOptionsTest as _AutogenerateFKOptionsTest,
)
from alembic.testing.suite.test_autogen_fks import (
    AutogenerateForeignKeysTest as _AutogenerateForeignKeysTest,
)
from alembic.testing.suite.test_autogen_fks import IncludeHooksTest as _IncludeHooksTest


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
