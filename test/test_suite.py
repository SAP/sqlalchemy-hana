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
from sqlalchemy import exc
from sqlalchemy.testing.suite import ExceptionTest as _ExceptionTest


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


class ExceptionTest(_ExceptionTest):

    @requirements.duplicate_key_raises_integrity_error
    def test_integrity_error(self):

        with config.db.begin() as conn:
            conn.execute(
                self.tables.manual_pk.insert(),
                {'id': 1, 'data': 'd1'}
            )
            try:
                assert_raises(
                    exc.IntegrityError,
                    conn.execute,
                    self.tables.manual_pk.insert(),
                    {'id': 1, 'data': 'd1'}
                )

            except exc.DBAPIError:
                from hdbcli.dbapi import IntegrityError
                raise IntegrityError