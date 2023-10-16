from __future__ import annotations

import sqlalchemy
import sqlalchemy.testing
from sqlalchemy.testing import eq_


class IsolationLevelTest(sqlalchemy.testing.fixtures.TestBase):
    __only_on__ = "hana"

    def _default_isolation_level(self):
        return "READ COMMITTED"

    def _non_default_isolation_level(self):
        return "SERIALIZABLE"

    def test_get_isolation_level(self):
        eng = sqlalchemy.testing.engines.testing_engine(options=dict())
        isolation_level = eng.dialect.get_isolation_level(eng.connect().connection)
        eq_(isolation_level, self._default_isolation_level())

    def test_set_isolation_level(self):
        eng = sqlalchemy.testing.engines.testing_engine(options=dict())
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._default_isolation_level(),
        )

        eng.dialect.set_isolation_level(
            conn.connection, self._non_default_isolation_level()
        )

        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._non_default_isolation_level(),
        )
        conn.close()

    def test_reset_level(self):
        eng = sqlalchemy.testing.engines.testing_engine(options=dict())
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._default_isolation_level(),
        )

        eng.dialect.set_isolation_level(
            conn.connection, self._non_default_isolation_level()
        )
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._non_default_isolation_level(),
        )

        eng.dialect.reset_isolation_level(conn.connection)
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._default_isolation_level(),
        )
        conn.close()

    def test_set_level_with_setting(self):
        eng = sqlalchemy.testing.engines.testing_engine(
            options=dict(isolation_level=self._non_default_isolation_level())
        )
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._non_default_isolation_level(),
        )

        eng.dialect.set_isolation_level(
            conn.connection, self._default_isolation_level()
        )
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._default_isolation_level(),
        )
        conn.close()

    def test_invalid_level(self):
        eng = sqlalchemy.testing.engines.testing_engine(
            options=dict(isolation_level="FOO")
        )
        sqlalchemy.testing.assert_raises_message(
            sqlalchemy.exc.ArgumentError,
            "Invalid value '%s' for isolation_level. "
            "Valid isolation levels for %s are %s"
            % ("FOO", eng.dialect.name, ", ".join(eng.dialect._isolation_lookup)),
            eng.connect,
        )

    def test_with_execution_options(self):
        eng = sqlalchemy.create_engine(
            sqlalchemy.testing.db.url,
            execution_options={"isolation_level": self._non_default_isolation_level()},
        )
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._non_default_isolation_level(),
        )
        conn.close()

    def test_with_isolation_level_in_create_engine(self):
        eng = sqlalchemy.create_engine(
            sqlalchemy.testing.db.url,
            isolation_level=self._non_default_isolation_level(),
        )
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            self._non_default_isolation_level(),
        )
        conn.close()
