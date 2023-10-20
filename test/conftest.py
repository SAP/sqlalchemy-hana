from __future__ import annotations

import logging

from sqlalchemy import Column, Sequence, event
from sqlalchemy.dialects import registry

logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

registry.register("hana", "sqlalchemy_hana.dialect", "HANAHDBCLIDialect")
registry.register("hana.hdbcli", "sqlalchemy_hana.dialect", "HANAHDBCLIDialect")


@event.listens_for(Column, "after_parent_attach")
def add_test_seq(column, table):
    if column.info.get("test_needs_autoincrement", False):
        column._init_items(Sequence(table.name + "_" + column.name + "_seq"))


# enable the SQLAlchemy plugin after our setup is done
import sqlalchemy.testing.plugin.pytestplugin  # noqa: F401,E402
