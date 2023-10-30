from __future__ import annotations

from sqlalchemy.testing.provision import temp_table_keyword_args
from sqlalchemy.testing.suite import *  # noqa: F401, F403

# Import dialect test suite provided by SQLAlchemy into SQLAlchemy-HANA test collection.
# Please don't add other tests in this file. Only adjust or overview SQLAlchemy tests
# for compatibility with SAP HANA.


@temp_table_keyword_args.for_db("*")
def _temp_table_keyword_args(*args, **kwargs):
    return {
        "prefixes": ["GLOBAL TEMPORARY"],
    }
