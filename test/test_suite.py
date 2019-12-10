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

from sqlalchemy import testing, create_engine
from sqlalchemy import column, table
from sqlalchemy.testing import engines, assert_raises_message
from sqlalchemy.testing.suite import *
from sqlalchemy.testing.exclusions import skip_if
from sqlalchemy.testing.mock import Mock
from sqlalchemy import event
from sqlalchemy.schema import DDL
from sqlalchemy.testing.assertions import AssertsCompiledSQL
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
        # the definition of temporary tables in the temporary table tests needs to be overwritten,
        # because similar to oracle, in HANA one needs to mention GLOBAL or LOCAL in the temporary table definition

        if testing.against("hana"):
            kw = {
                'prefixes': ["GLOBAL TEMPORARY"],
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

    @testing.provide_metadata
    def _test_get_table_oid(self, table_name, schema=None):
        meta = self.metadata
        insp = inspect(meta.bind)
        oid = insp.get_table_oid(table_name, schema)
        self.assert_(isinstance(oid, int))

    @testing.requires.foreign_key_constraint_option_reflection
    @testing.provide_metadata
    def test_get_foreign_key_options(self):
        # this tests needs to be overwritten, because
        # In no case in SQLAlchemy-hana an empty dictionary is returned for foreign key options.
        # Also if the user does not explicitly mention the referential actions to be used in the
        # create table statement, the default values of the referential actions in HANA (RESTRICT) are reflected.
        meta = self.metadata

        Table(
            'x', meta,
            Column('id', Integer, primary_key=True),
            test_needs_fk=True
        )

        Table('table', meta,
              Column('id', Integer, primary_key=True),
              Column('x_id', Integer, sa.ForeignKey('x.id', name='xid')),
              Column('test', String(10)),
              test_needs_fk=True)

        Table('user', meta,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('tid', Integer),
              sa.ForeignKeyConstraint(
                  ['tid'], ['table.id'],
                  name='myfk',
                  onupdate="SET NULL", ondelete="CASCADE"),
                  test_needs_fk=True)

        meta.create_all()

        insp = inspect(meta.bind)

        opts = insp.get_foreign_keys('user')[0]['options']
        eq_(
            dict(
                (k, opts[k])
                for k in opts if opts[k]
            ),
            {'onupdate': 'SET NULL', 'ondelete': 'CASCADE'}
        )
class IsolationLevelTest(fixtures.TestBase):

    def _default_isolation_level(self):
        return 'READ COMMITTED'

    def _non_default_isolation_level(self):
        return 'SERIALIZABLE'

    @testing.only_on('hana')
    def test_get_isolation_level(self):
        eng = engines.testing_engine(options=dict())
        isolation_level = eng.dialect.get_isolation_level(
            eng.connect().connection)
        eq_(
            isolation_level,
            self._default_isolation_level()
        )

    @testing.only_on('hana')
    @testing.only_if('hana+hdbcli')
    def test_set_isolation_level(self):
        eng = engines.testing_engine(options=dict())
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._default_isolation_level()
        )

        eng.dialect.set_isolation_level(
            conn.connection, self._non_default_isolation_level()
        )

        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._non_default_isolation_level()
        )
        conn.close()

    @testing.only_on('hana')
    @testing.only_if('hana+hdbcli')
    def test_reset_level(self):
        eng = engines.testing_engine(options=dict())
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._default_isolation_level()
        )

        eng.dialect.set_isolation_level(
            conn.connection, self._non_default_isolation_level()
        )
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._non_default_isolation_level()
        )

        eng.dialect.reset_isolation_level(conn.connection)
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._default_isolation_level()
        )
        conn.close()

    @testing.only_on('hana')
    @testing.only_if('hana+hdbcli')
    def test_set_level_with_setting(self):
        eng = engines.testing_engine(options=dict(isolation_level=self._non_default_isolation_level()))
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._non_default_isolation_level()
        )

        eng.dialect.set_isolation_level(conn.connection, self._default_isolation_level())
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._default_isolation_level()
        )
        conn.close()

    @testing.only_on('hana')
    @testing.only_if('hana+hdbcli')
    def test_invalid_level(self):
        eng = engines.testing_engine(options=dict(isolation_level='FOO'))
        assert_raises_message(
            exc.ArgumentError,
            "Invalid value '%s' for isolation_level. "
            "Valid isolation levels for %s are %s" %
            ("FOO", eng.dialect.name, ", ".join(eng.dialect._isolation_lookup)), eng.connect
        )

    @testing.only_on('hana')
    @testing.only_if('hana+hdbcli')
    def test_with_execution_options(self):
        eng = create_engine(
            testing.db.url,
            execution_options={'isolation_level': self._non_default_isolation_level()}
            )
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._non_default_isolation_level()
        )
        conn.close()

    @testing.only_on('hana')
    @testing.only_if('hana+hdbcli')
    def test_with_isolation_level_in_create_engine(self):
        eng = create_engine(
            testing.db.url,
            isolation_level=self._non_default_isolation_level()
            )
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._non_default_isolation_level()
        )
        conn.close()

class HANAConnectUrlUserHDBUserStoreTest(fixtures.TestBase):

    @testing.only_on('hana')
    @testing.only_if('hana+hdbcli')
    def test_parsing_userkey_hdbcli(self):
        import sqlalchemy.engine.url

        dialect = testing.db.dialect

        _, result_kwargs = dialect.create_connect_args(sqlalchemy.engine.url.make_url("hana://userkey=myhxe"))
        assert result_kwargs['userkey'] == "myhxe"


    @testing.only_on('hana')
    @testing.only_if('hana+pyhdb')
    def test_parsing_userkey_pyhdb(self):
        import sqlalchemy.engine.url

        dialect = testing.db.dialect

        assert_raises(NotImplementedError, dialect.create_connect_args, sqlalchemy.engine.url.make_url("hana+pyhdb://userkey=myhxe"))


class HANAConnectUrlParsing(fixtures.TestBase):

    @testing.only_on('hana')
    @testing.only_if('hana+hdbcli')
    def test_pass_uri_query_as_kwargs(self):
        """Verify sqlalchemy-hana passes all uri query parameters to hdbcli"""
        import sqlalchemy.engine.url

        dialect = testing.db.dialect

        _, kwargs = dialect.create_connect_args(
            sqlalchemy.engine.url.make_url(
                "hana+hdbcli://user:password@example.com/my-database?encrypt=true&compress=true"
            )
        )
        assert kwargs["encrypt"] == "true"
        assert kwargs["compress"] == "true"


class HANACompileTest(fixtures.TestBase, AssertsCompiledSQL):

    __dialect__ = testing.db.dialect

    @testing.only_on('hana')
    @testing.only_if('hana+hdbcli')
    def test_sql_row_locking(self):
        table1 = table(
            "mytable", column("myid"), column("name"), column("description")
        )

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
            table1.select().with_for_update(skip_locked=True),
            "SELECT mytable.myid, mytable.name, mytable.description "
            "FROM mytable FOR UPDATE IGNORE LOCKED",
        )
