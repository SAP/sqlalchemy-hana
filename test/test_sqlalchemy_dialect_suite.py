from __future__ import annotations

import sqlalchemy
from sqlalchemy.testing.suite import ComponentReflectionTest as _ComponentReflectionTest
from sqlalchemy.testing.suite import *  # noqa: F401, F403

# Import dialect test suite provided by SQLAlchemy into SQLAlchemy-HANA test collection.
# Please don't add other tests in this file. Only adjust or overview SQLAlchemy tests
# for compatibility with SAP HANA.


class ComponentReflectionTest(_ComponentReflectionTest):
    # Overwrite function so that temporary tables are correctly created with HANA's specific
    # GLOBAL prefix.
    @classmethod
    def define_temp_tables(cls, metadata):
        kw = {
            "prefixes": ["GLOBAL TEMPORARY"],
        }

        sqlalchemy.Table(
            "user_tmp",
            metadata,
            sqlalchemy.Column("id", sqlalchemy.INT, primary_key=True),
            sqlalchemy.Column("name", sqlalchemy.VARCHAR(50)),
            sqlalchemy.Column("foo", sqlalchemy.INT),
            sqlalchemy.UniqueConstraint("name", name="user_tmp_uq"),
            sqlalchemy.Index("user_tmp_ix", "foo"),
            **kw,
        )

    # Overwrite function as SQLAlchemy assumes only the PostgreSQL dialect allows to retrieve the
    # table object id but SQLAlchemy-HANA also provides this functionality.
    @sqlalchemy.testing.provide_metadata
    def _test_get_table_oid(self, table_name, schema=None):
        meta = self.metadata
        insp = sqlalchemy.inspect(meta.bind)
        oid = insp.get_table_oid(table_name, schema)
        self.assert_(isinstance(oid, int))
