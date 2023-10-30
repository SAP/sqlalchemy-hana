from __future__ import annotations

from unittest.mock import Mock

import sqlalchemy.testing


class HANAHDBCLIConnectionIsDisconnectedTest(sqlalchemy.testing.fixtures.TestBase):
    __only_on__ = "hana+hdbcli"

    def test_detection_by_error_code(self):
        from hdbcli.dbapi import Error

        dialect = sqlalchemy.testing.db.dialect
        assert dialect.is_disconnect(Error(-10709, "Connect failed"), None, None)

    def test_detection_by_isconnected_function(self):
        dialect = sqlalchemy.testing.db.dialect

        mock_connection = Mock(isconnected=Mock(return_value=False))
        assert dialect.is_disconnect(None, mock_connection, None)

        mock_connection = Mock(isconnected=Mock(return_value=True))
        assert not dialect.is_disconnect(None, mock_connection, None)
