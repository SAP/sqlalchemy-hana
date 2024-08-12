"""Custom error handling testing."""

from __future__ import annotations

import pytest
from hdbcli.dbapi import Error as HdbcliError
from sqlalchemy.exc import DBAPIError
from sqlalchemy.testing.fixtures import TestBase

from sqlalchemy_hana.errors import (
    ClientConnectionError,
    DatabaseConnectNotPossibleError,
    DatabaseOutOfMemoryError,
    DatabaseOverloadedError,
    DeadlockError,
    InvalidObjectNameError,
    LockAcquisitionError,
    LockWaitTimeoutError,
    SequenceCacheTimeoutError,
    SequenceLockTimeoutError,
    StatementExecutionError,
    StatementTimeoutError,
    TransactionCancelledError,
    WriteInReadOnlyReplicationError,
    convert_dbapi_error,
)


class TestConvertDBAPIError(TestBase):
    @pytest.mark.parametrize(
        "errorcode,errortext,expected_exception",
        [
            (-10807, "", ClientConnectionError),
            (-10709, "", ClientConnectionError),
            (
                99999,
                "Lock timeout occurs while waiting sequence cache lock",
                SequenceCacheTimeoutError,
            ),
            (
                131,
                "transaction rolled back: Lock timeout occurs while waiting sequence lock",
                SequenceLockTimeoutError,
            ),
            (131, "", LockWaitTimeoutError),
            (146, "", LockAcquisitionError),
            (133, "", DeadlockError),
            (4, "no memory", DatabaseOutOfMemoryError),
            (99999, "OutOfMemory exception", DatabaseOutOfMemoryError),
            (99999, "cannot allocate enough memory", DatabaseOutOfMemoryError),
            (99999, "Allocation failed", DatabaseOutOfMemoryError),
            (
                129,
                "max number of SqlExecutor threads are exceeded",
                DatabaseOverloadedError,
            ),
            (
                663,
                "Error GBA503: Service is unavailable",
                DatabaseConnectNotPossibleError,
            ),
            (
                1897,
                "HANA Cloud region is in maintenance window",
                DatabaseConnectNotPossibleError,
            ),
            (
                129,
                "An error occurred while opening the channel",
                StatementExecutionError,
            ),
            (
                2048,
                "An error occurred while opening the channel",
                StatementExecutionError,
            ),
            (
                139,
                "Error: current operation cancelled by request and transaction rolled back",
                TransactionCancelledError,
            ),
            (613, "", StatementTimeoutError),
            (397, "", InvalidObjectNameError),
            (
                7,
                "feature not supported: writable statement not allowed in "
                "read-enabled replication: line 1 col 1",
                WriteInReadOnlyReplicationError,
            ),
        ],
    )
    def test_convert_dbapi_error(
        self,
        errorcode: int,
        errortext: str,
        expected_exception: type[Exception],
    ) -> None:
        error = HdbcliError(errorcode, errortext)
        dbapi_error = DBAPIError(None, None, error)
        assert isinstance(convert_dbapi_error(dbapi_error), expected_exception)

    @pytest.mark.parametrize(
        "errorcode,errortext",
        [
            (123, "An error occurred while doing something"),
            (-10800, ""),
            (123, "some error"),
        ],
    )
    def test_convert_dbapi_error_no_wrap(self, errorcode: int, errortext: str) -> None:
        error = HdbcliError(errorcode, errortext)
        dbapi_error = DBAPIError(None, None, error)
        assert convert_dbapi_error(dbapi_error) is dbapi_error
