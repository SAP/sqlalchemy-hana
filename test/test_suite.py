# Copyright 2015 SAP SE.
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

# test/test_suite.py

from sqlalchemy import testing
from sqlalchemy.testing import engines
from sqlalchemy.testing.suite import *
from sqlalchemy.testing.exclusions import skip_if
from sqlalchemy.testing.mock import Mock
from sqlalchemy import event
from sqlalchemy.schema import DDL
from sqlalchemy.testing.suite import ComponentReflectionTest as _ComponentReflectionTest
import sqlalchemy as sa
from sqlalchemy import inspect


class HANAConnectionIsDisconnectedTest(fixtures.TestBase):

    @testing.only_on('hana')
    @testing.skip_if('hana+pyhdb')
    def test_detection_by_error_code(self):
        from hdbcli.dbapi import Error

        dialect = testing.db.dialect
        assert dialect.is_disconnect(Error(-10709, 'Connect failed'), None, None)

    @testing.only_on('hana')
    @testing.skip_if('hana+pyhdb')
    def test_detection_by_isconnected_function(self):
        dialect = testing.db.dialect

        mock_connection = Mock(
            isconnected=Mock(return_value=False)
        )
        assert dialect.is_disconnect(None, mock_connection, None)

        mock_connection = Mock(
            isconnected=Mock(return_value=True)
        )
        assert not dialect.is_disconnect(None, mock_connection, None)

class HANAConnectUrlHasTenantTest(fixtures.TestBase):

    @testing.only_on('hana')
    @testing.only_if('hana+hdbcli')
    def test_tenant_url_parsing_hdbcli(self):
        import sqlalchemy.engine.url

        dialect = testing.db.dialect

        _, result_kwargs = dialect.create_connect_args(sqlalchemy.engine.url.make_url("hana://USER:PASS@HOST/TNT"))
        assert result_kwargs['databaseName'] == "TNT"

    @testing.only_on('hana')
    @testing.only_if('hana+pyhdb')
    def test_tenant_url_parsing_pyhdb(self):
        import sqlalchemy.engine.url

        dialect = testing.db.dialect

        assert_raises(NotImplementedError, dialect.create_connect_args, sqlalchemy.engine.url.make_url("hana://USER:PASS@HOST/TNT"))

class ComponentReflectionTest(_ComponentReflectionTest):

    @classmethod
    def define_temp_tables(cls, metadata):
        if testing.against("hana"):
            kw = {
                'prefixes': ["GLOBAL TEMPORARY"],
                'oracle_on_commit': 'PRESERVE ROWS'
            }
        else:
            kw = {
                'prefixes': ["TEMPORARY"],
            }

        user_tmp = Table(
            "user_tmp", metadata,
            Column("id", sa.INT, primary_key=True),
            Column('name', sa.VARCHAR(50)),
            Column('foo', sa.INT),
            sa.UniqueConstraint('name', name='user_tmp_uq'),
            sa.Index("user_tmp_ix", "foo"),
            **kw
        )
        if testing.requires.view_reflection.enabled and \
                testing.requires.temporary_views.enabled:
            event.listen(
                user_tmp, "after_create",
                DDL("create temporary view user_tmp_v as "
                    "select * from user_tmp")
            )
            event.listen(
                user_tmp, "before_drop",
                DDL("drop view user_tmp_v")
            )

    @skip_if('hana')
    @testing.requires.temp_table_reflection
    @testing.requires.unique_constraint_reflection
    def test_get_temp_table_unique_constraints(self):
        insp = inspect(self.bind)
        reflected = insp.get_unique_constraints('user_tmp')
        for refl in reflected:
            refl.pop('duplicates_index', None)
        eq_(reflected, [{'column_names': ['name'], 'name': 'user_tmp_uq'}])

    @testing.provide_metadata
    def _test_get_table_oid(self, table_name, schema=None):
        meta = self.metadata
        insp = inspect(meta.bind)
        oid = insp.get_table_oid(table_name, schema)
        self.assert_(isinstance(oid, int))

class HANAConnectUrlUserHDBUserStoreTest(fixtures.TestBase):

    @testing.only_on('hana')
    @testing.only_if('hana+hdbcli')
    def test_tenant_url_parsing_hdbcli(self):
        import sqlalchemy.engine.url

        dialect = testing.db.dialect

        _, result_kwargs = dialect.create_connect_args(sqlalchemy.engine.url.make_url("hana://userkey=myhxe"))
        assert result_kwargs['userkey'] == "myhxe"


    @testing.only_on('hana')
    @testing.only_if('hana+pyhdb')
    def test_tenant_url_parsing_pyhdb(self):
        import sqlalchemy.engine.url

        dialect = testing.db.dialect

        assert_raises(NotImplementedError, dialect.create_connect_args, sqlalchemy.engine.url.make_url("hana+pyhdb://userkey=myhxe"))
        
        # _, result_kwargs = dialect.create_connect_args(sqlalchemy.engine.url.make_url("hana+pyhdb://userkey=myhxe"))
        # assert result_kwargs['userkey'] == "myhxe"
        # assert dialect.is_disconnect(Error(-10709, 'Connect failed'), None, None)
        # assert_raises_message(NotImplementedError, 'no support for HDB user store')