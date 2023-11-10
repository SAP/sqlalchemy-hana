# pylint: disable=wildcard-import,unused-wildcard-import,wrong-import-position
"""Pytest test configuration."""

from __future__ import annotations

import logging
import random
import string
from typing import Any

import pytest
from sqlalchemy import Column, Sequence, Table, event, text
from sqlalchemy.dialects import registry

# isort: off

logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

registry.register("hana", "sqlalchemy_hana.dialect", "HANAHDBCLIDialect")
pytest.register_assert_rewrite("sqlalchemy.testing.assertions")
pytest.register_assert_rewrite("alembic.testing.assertions")


@event.listens_for(Column, "after_parent_attach")
def add_test_seq(column: Column, table: Table) -> None:
    if column.info.get("test_needs_autoincrement", False):
        column._init_items(Sequence(table.name + "_" + column.name + "_seq"))


# imports used for customizations, need to be imported AFTER SQLAlchemy plugin setup
from sqlalchemy.testing.plugin.pytestplugin import *  # noqa: F403,F401,E402

# enable the SQLAlchemy plugin after our setup is done
from sqlalchemy import testing  # noqa: E402
from sqlalchemy.testing.config import Config  # noqa: E402
from sqlalchemy.testing.plugin.plugin_base import post  # noqa: E402

TEST_SCHEMA = TEST_SCHEMA2 = ""


def _get_main_config() -> Config:
    assert len(Config.all_configs()) == 1, "only one present config is expected"
    return list(Config.all_configs())[0]


def _random_string(length: int) -> str:
    """Create a random string with the given length."""
    return "CI_" + "".join(random.choices(string.ascii_lowercase, k=length))


@post
def randomize_test_schemas(*args: Any, **kwargs: Any) -> None:
    """Set random schema names for the testing schemas."""
    # pylint: disable=global-statement
    global TEST_SCHEMA, TEST_SCHEMA2

    config = _get_main_config()
    config.test_schema = TEST_SCHEMA = _random_string(10)
    config.test_schema_2 = TEST_SCHEMA2 = _random_string(10)
    Config.set_as_current(config, testing)
    testing.config.ident = _random_string(5)

    # we don't need to drop the schemas later,
    # because the user is dropped later and with it the schemas
    with config.db.connect() as connection, connection.begin():
        for schema in [config.test_schema, config.test_schema_2]:
            connection.execute(text(f"CREATE SCHEMA {schema}"))


@pytest.fixture(autouse=True)
def set_test_schemas() -> None:
    """Set the right test schemas before each test."""
    config = _get_main_config()
    config.test_schema = TEST_SCHEMA
    config.test_schema_2 = TEST_SCHEMA2
    Config.set_as_current(config, testing)
