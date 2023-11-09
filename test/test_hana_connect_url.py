"""SAP HANA URL testing."""

from __future__ import annotations

import pytest
import sqlalchemy.testing
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url


class HANAConnectUrlTest(sqlalchemy.testing.fixtures.TestBase):
    def test_hdbcli_tenant_url_default_port(self) -> None:
        """If the URL includes a tenant database, the dialect pass the adjusted values to hdbcli.

        Beside the parameter databaseName, it should also adjust the default port to the SYSTEMDB
        SQL port for HANA's automated tenant redirect as the SQL ports of tenant datbases are are
        transient.
        """

        _, result_kwargs = sqlalchemy.testing.db.dialect.create_connect_args(
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

        _, result_kwargs = sqlalchemy.testing.db.dialect.create_connect_args(
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

        _, result_kwargs = sqlalchemy.testing.db.dialect.create_connect_args(
            make_url("hana://userkey=myuserkeyname")
        )
        assert result_kwargs == {"userkey": "myuserkeyname"}

    def test_pass_uri_query_as_kwargs(self) -> None:
        """SQLAlchemy-HANA should passes all URL parameters to hdbcli."""

        urls = [
            "hana://username:secret-password@example.com/?encrypt=true&compress=true",
            "hana://username:secret-password@example.com/TENANT_NAME?encrypt=true&compress=true",
        ]

        for url in urls:
            _, result_kwargs = sqlalchemy.testing.db.dialect.create_connect_args(
                make_url(url)
            )
            assert result_kwargs["encrypt"] == "true"
            assert result_kwargs["compress"] == "true"


class HANACreateEngineTest(sqlalchemy.testing.fixtures.TestBase):
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
