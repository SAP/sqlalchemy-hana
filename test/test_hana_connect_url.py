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

import sqlalchemy.testing
from sqlalchemy.engine.url import make_url


class HANAConnectUrlWithTenantTest(sqlalchemy.testing.fixtures.TestBase):

    @sqlalchemy.testing.only_on('hana+hdbcli')
    def test_hdbcli_tenant_url_default_port(self):
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
        assert result_kwargs['databaseName'] == "TENANT_NAME"

    @sqlalchemy.testing.only_on('hana+hdbcli')
    def test_hdbcli_tenant_url_changed_port(self):
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
        assert result_kwargs['databaseName'] == "TENANT_NAME"

    @sqlalchemy.testing.only_on('hana+pyhdb')
    def test_pyhdb_rejects_tenant_names(self):
        """PyHDB doesn't support connecting to database tenants via their name.
        The user must provide the correct SQL port. A NotImplementedError notifies the user.
        """

        sqlalchemy.testing.assert_raises(
            NotImplementedError,
            sqlalchemy.testing.db.dialect.create_connect_args,
            make_url("hana://username:secret-password@example.com/TENANT_NAME")
        )


class HANAConnectUrlWithHDBUserStoreTest(sqlalchemy.testing.fixtures.TestBase):

    @sqlalchemy.testing.only_on('hana+hdbcli')
    def test_parsing_userkey_hdbcli(self):
        """With HDBCLI, the user may reference to a local HDBUserStore key which holds
        the connection details. SQLAlchemy-HANA should only pass the userkey name to
        HDBCLI for the connection creation.
        """

        _, result_kwargs = sqlalchemy.testing.db.dialect.create_connect_args(
            make_url("hana://userkey=myuserkeyname")
        )
        assert result_kwargs == {"userkey": "myuserkeyname"}


    @sqlalchemy.testing.only_on('hana+pyhdb')
    def test_parsing_userkey_pyhdb(self):
        """PyHDB doesn't support the HDBUserStore and should raise a NotImplementedError."""

        sqlalchemy.testing.assert_raises(
            NotImplementedError,
            sqlalchemy.testing.db.dialect.create_connect_args,
            make_url("hana://userkey=myuserkeyname")
        )


class HANAConnectUrlParsing(sqlalchemy.testing.fixtures.TestBase):

    @sqlalchemy.testing.only_on('hana+hdbcli')
    def test_pass_uri_query_as_kwargs(self):
        """SQLAlchemy-HANA should passes all URL parameters to hdbcli."""

        urls = [
            "hana://username:secret-password@example.com/?encrypt=true&compress=true",
            "hana://username:secret-password@example.com/TENANT_NAME?encrypt=true&compress=true"
        ]

        for url in urls:
            _, result_kwargs = sqlalchemy.testing.db.dialect.create_connect_args(
                make_url(url)
            )
            assert result_kwargs["encrypt"] == "true"
            assert result_kwargs["compress"] == "true"
