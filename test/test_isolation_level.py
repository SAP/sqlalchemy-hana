"""SAP HANA isolation level testing."""


from __future__ import annotations

import sqlalchemy
import sqlalchemy.testing
from sqlalchemy.testing import eq_
from sqlalchemy.testing.assertions import assert_raises_message
from sqlalchemy.testing.engines import testing_engine


class IsolationLevelTest(sqlalchemy.testing.fixtures.TestBase):
    def _default_isolation_level(self) -> str:
        return "READ COMMITTED"

    def _non_default_isolation_level(self) -> str:
        return "SERIALIZABLE"

    def test_get_isolation_level(self) -> None:
        eng = sqlalchemy.testing.engines.testing_engine(options={})
        isolation_level = eng.dialect.get_isolation_level(eng.connect().connection)
        eq_(isolation_level, self._default_isolation_level())

    def test_set_isolation_level(self) -> None:
        eng = sqlalchemy.testing.engines.testing_engine(options={})
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

    def test_reset_level(self) -> None:
        eng = sqlalchemy.testing.engines.testing_engine(options={})
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

    def test_set_level_with_setting(self) -> None:
        eng = sqlalchemy.testing.engines.testing_engine(
            options={"isolation_level": self._non_default_isolation_level()}
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

    def test_invalid_level(self) -> None:
        eng = testing_engine(options={"isolation_level": "FOO"})
        levels = ", ".join(eng.dialect._isolation_lookup)
        assert_raises_message(
            sqlalchemy.exc.ArgumentError,
            "Invalid value 'FOO' for isolation_level. "
            f"Valid isolation levels for {eng.dialect.name} are {levels}",
            eng.connect,
        )

    def test_with_execution_options(self) -> None:
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

    def test_with_isolation_level_in_create_engine(self) -> None:
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
