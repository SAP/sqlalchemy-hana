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
from sqlalchemy.testing.mock import Mock

class HANAHDBCLIConnectionIsDisconnectedTest(sqlalchemy.testing.fixtures.TestBase):

    __only_on__ = "hana+hdbcli"

    def test_detection_by_error_code(self):
        from hdbcli.dbapi import Error

        dialect = sqlalchemy.testing.db.dialect
        assert dialect.is_disconnect(Error(-10709, 'Connect failed'), None, None)

    def test_detection_by_isconnected_function(self):
        dialect = sqlalchemy.testing.db.dialect

        mock_connection = Mock(
            isconnected=Mock(return_value=False)
        )
        assert dialect.is_disconnect(None, mock_connection, None)

        mock_connection = Mock(
            isconnected=Mock(return_value=True)
        )
        assert not dialect.is_disconnect(None, mock_connection, None)
