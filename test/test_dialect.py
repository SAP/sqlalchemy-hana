"""SAP HANA Dialect testing."""

from __future__ import annotations

import sys
from unittest import mock
from unittest.mock import Mock

import pytest
from hdbcli.dbapi import Error
from sqlalchemy import create_engine
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ArgumentError, DBAPIError
from sqlalchemy.testing import assert_raises_message, config, eq_
from sqlalchemy.testing.engines import testing_engine
from sqlalchemy.testing.fixtures import TestBase

DEFAULT_ISOLATION_LEVEL = "READ COMMITTED"
NON_DEFAULT_ISOLATION_LEVEL = "SERIALIZABLE"


class DialectTest(TestBase):
    def test_detection_by_error_code(self) -> None:
        dialect = config.db.dialect
        assert dialect.is_disconnect(Error(-10709, "Connect failed"), None, None)

    def test_detection_by_isconnected_function(self) -> None:
        dialect = config.db.dialect

        mock_connection = Mock(isconnected=Mock(return_value=False))
        assert dialect.is_disconnect(None, mock_connection, None)

        mock_connection = Mock(isconnected=Mock(return_value=True))
        assert not dialect.is_disconnect(None, mock_connection, None)

    @pytest.mark.parametrize(
        "kwargs,supports_native_boolean",
        [
            ({}, True),
            ({"use_native_boolean": True}, True),
            ({"use_native_boolean": False}, False),
        ],
    )
    def test_supports_native_boolean(
        self, kwargs: dict, supports_native_boolean: bool
    ) -> None:
        engine = create_engine("hana://username:secret-password@example.com", **kwargs)
        assert engine.dialect.supports_native_boolean == supports_native_boolean

    def test_hdbcli_tenant_url_default_port(self) -> None:
        """If the URL includes a tenant database, the dialect pass the adjusted values to hdbcli.

        Beside the parameter databaseName, it should also adjust the default port to the SYSTEMDB
        SQL port for HANA's automated tenant redirect as the SQL ports of tenant datbases are are
        transient.
        """
        _, result_kwargs = config.db.dialect.create_connect_args(
            make_url("hana://username:secret-password@example.com/TENANT_NAME")
        )
        assert result_kwargs["address"] == "example.com"
        assert result_kwargs["port"] == 30013
        assert result_kwargs["user"] == "username"
        assert result_kwargs["password"] == "secret-password"
        assert result_kwargs["databaseName"] == "TENANT_NAME"

    def test_hdbcli_tenant_url_changed_port(self) -> None:
        """If the URL includes a tenant database, the dialect pass the adjusted values to hdbcli.

        It doesn't adjust the port if the user explicitly defined it.
        """
        _, result_kwargs = config.db.dialect.create_connect_args(
            make_url("hana://username:secret-password@example.com:30041/TENANT_NAME")
        )
        assert result_kwargs["address"] == "example.com"
        assert result_kwargs["port"] == 30041
        assert result_kwargs["user"] == "username"
        assert result_kwargs["password"] == "secret-password"
        assert result_kwargs["databaseName"] == "TENANT_NAME"

    def test_parsing_userkey_hdbcli(self) -> None:
        """With HDBCLI, the user may reference to a local HDBUserStore key which holds
        the connection details. SQLAlchemy-HANA should only pass the userkey name to
        HDBCLI for the connection creation.
        """
        _, result_kwargs = config.db.dialect.create_connect_args(
            make_url("hana://userkey=myuserkeyname")
        )
        assert result_kwargs == {"userkey": "myuserkeyname", "vectoroutputtype": "list"}

    def test_pass_uri_query_as_kwargs(self) -> None:
        """SQLAlchemy-HANA should passes all URL parameters to hdbcli."""
        urls = [
            "hana://username:secret-password@example.com/?encrypt=true&compress=true",
            "hana://username:secret-password@example.com/TENANT_NAME?encrypt=true&compress=true",
        ]

        for url in urls:
            _, result_kwargs = config.db.dialect.create_connect_args(make_url(url))
            assert result_kwargs["encrypt"] == "true"
            assert result_kwargs["compress"] == "true"

    def test_server_version_info(self) -> None:
        # Test that the attribute is defined
        assert config.db.dialect.server_version_info

    def test_get_isolation_level(self) -> None:
        eng = testing_engine(options={})
        isolation_level = eng.dialect.get_isolation_level(eng.connect().connection)
        eq_(isolation_level, DEFAULT_ISOLATION_LEVEL)

    def test_set_isolation_level(self) -> None:
        eng = testing_engine(options={})
        conn = eng.connect()
        eq_(eng.dialect.get_isolation_level(conn.connection), DEFAULT_ISOLATION_LEVEL)

        eng.dialect.set_isolation_level(conn.connection, NON_DEFAULT_ISOLATION_LEVEL)

        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            NON_DEFAULT_ISOLATION_LEVEL,
        )
        conn.close()

    def test_reset_level(self) -> None:
        eng = testing_engine(options={})
        conn = eng.connect()
        eq_(eng.dialect.get_isolation_level(conn.connection), DEFAULT_ISOLATION_LEVEL)

        eng.dialect.set_isolation_level(conn.connection, NON_DEFAULT_ISOLATION_LEVEL)
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            NON_DEFAULT_ISOLATION_LEVEL,
        )

        eng.dialect.reset_isolation_level(conn.connection)
        eq_(eng.dialect.get_isolation_level(conn.connection), DEFAULT_ISOLATION_LEVEL)
        conn.close()

    def test_set_level_with_setting(self) -> None:
        eng = testing_engine(options={"isolation_level": NON_DEFAULT_ISOLATION_LEVEL})
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            NON_DEFAULT_ISOLATION_LEVEL,
        )

        eng.dialect.set_isolation_level(conn.connection, DEFAULT_ISOLATION_LEVEL)
        eq_(eng.dialect.get_isolation_level(conn.connection), DEFAULT_ISOLATION_LEVEL)
        conn.close()

    def test_invalid_level(self) -> None:
        eng = testing_engine(options={"isolation_level": "FOO"})
        levels = ", ".join(eng.dialect._isolation_lookup)
        assert_raises_message(
            ArgumentError,
            "Invalid value 'FOO' for isolation_level. "
            f"Valid isolation levels for {eng.dialect.name} are {levels}",
            eng.connect,
        )

    def test_with_execution_options(self) -> None:
        eng = create_engine(
            config.db.url,
            execution_options={"isolation_level": NON_DEFAULT_ISOLATION_LEVEL},
        )
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            NON_DEFAULT_ISOLATION_LEVEL,
        )
        conn.close()

    def test_with_isolation_level_in_create_engine(self) -> None:
        eng = create_engine(config.db.url, isolation_level=NON_DEFAULT_ISOLATION_LEVEL)
        conn = eng.connect()
        eq_(
            eng.dialect.get_isolation_level(conn.connection),
            NON_DEFAULT_ISOLATION_LEVEL,
        )
        conn.close()

    def test_do_rollback_to_savepoint_no_error(self) -> None:
        dialect = config.db.dialect
        connection = Mock()

        with mock.patch.object(
            DefaultDialect, "do_rollback_to_savepoint"
        ) as super_rollback:
            dialect.do_rollback_to_savepoint(connection, "savepoint")
            super_rollback.assert_called_once_with(connection, "savepoint")

    def test_do_rollback_to_savepoint_unrelated_error(self) -> None:
        dialect = config.db.dialect
        connection = Mock()

        with (
            mock.patch.object(
                sys, "exc_info", return_value=(ValueError, ValueError(), Mock())
            ),
            mock.patch.object(
                DefaultDialect, "do_rollback_to_savepoint"
            ) as super_rollback,
        ):
            dialect.do_rollback_to_savepoint(connection, "savepoint")
            super_rollback.assert_called_once_with(connection, "savepoint")

    def test_do_rollback_to_savepoint_ignores_error(self) -> None:
        dialect = config.db.dialect
        connection = Mock()

        error = Error(133, "transaction rolled back: deadlock")
        dbapi_error = DBAPIError(None, None, error)

        with (
            mock.patch.object(
                sys, "exc_info", return_value=(DBAPIError, dbapi_error, Mock())
            ),
            mock.patch.object(
                DefaultDialect, "do_rollback_to_savepoint"
            ) as super_rollback,
        ):
            dialect.do_rollback_to_savepoint(connection, "savepoint")
            super_rollback.assert_not_called()

    def test_vectoroutputtype_is_blocked(self) -> None:
        url = "hana://username:secret-password@example.com/?encrypt=true&vectoroutputtype=list"
        with pytest.raises(ValueError, match="vectoroutputtype"):
            config.db.dialect.create_connect_args(make_url(url))

    @pytest.mark.parametrize(
        "kwargs,vector_output_type",
        [
            ({}, "list"),
            ({"vector_output_type": "list"}, "list"),
            ({"vector_output_type": "memoryview"}, "memoryview"),
        ],
    )
    def test_vector_output_type(self, kwargs: dict, vector_output_type: str) -> None:
        engine = create_engine("hana://username:secret-password@example.com", **kwargs)
        assert engine.dialect.vector_output_type == vector_output_type
