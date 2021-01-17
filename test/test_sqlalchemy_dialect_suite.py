# Copyright 2021 SAP SE.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http: //www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import sqlalchemy

# Import dialect test suite provided by SQLAlchemy into SQLAlchemy-HANA test collection.
# Please don't add other tests in this file. Only adjust or overview SQLAlchemy tests
# for compatibility with SAP HANA.

from sqlalchemy.testing.suite import *
from sqlalchemy.testing.suite import ComponentReflectionTest as _ComponentReflectionTest

class ComponentReflectionTest(_ComponentReflectionTest):

    # Overwrite function so that temporary tables are correctly created with HANA's specific
    # GLOBAL prefix.
    @classmethod
    def define_temp_tables(cls, metadata):
        kw = {
            'prefixes': ["GLOBAL TEMPORARY"],
        }

        Table(
            "user_tmp", metadata,
            Column("id", sqlalchemy.INT, primary_key=True),
            Column('name', sqlalchemy.VARCHAR(50)),
            Column('foo', sqlalchemy.INT),
            sqlalchemy.UniqueConstraint('name', name='user_tmp_uq'),
            sqlalchemy.Index("user_tmp_ix", "foo"),
            **kw
        )

    # Overwrite function as SQLAlchemy assumes only the PostgreSQL dialect allows to retrieve the
    # table object id but SQLAlchemy-HANA also provides this functionality.
    @sqlalchemy.testing.provide_metadata
    def _test_get_table_oid(self, table_name, schema=None):
        meta = self.metadata
        insp = sqlalchemy.inspect(meta.bind)
        oid = insp.get_table_oid(table_name, schema)
        self.assert_(isinstance(oid, int))
