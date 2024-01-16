"""Custom error handling testing."""

from __future__ import annotations

from unittest import mock

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
    LockAcquisitionError,
    LockWaitTimeoutError,
    SequenceCacheTimeoutError,
    StatementExecutionError,
    StatementTimeoutError,
    TransactionCancelledError,
    wrap_dbapi_error,
    wrap_hdbcli_error,
)


class TestWrapDbapiError(TestBase):
    def test_calls_wrap_hdbcli_error(self) -> None:
        hdbcli_error = HdbcliError()
        error = DBAPIError("", None, orig=hdbcli_error)

        with mock.patch("sqlalchemy_hana.errors.wrap_hdbcli_error") as mocked:
            wrap_dbapi_error(error)

        mocked.assert_called_once_with(hdbcli_error)

    def test_calls_not_wrap_hdbcli_error(self) -> None:
        error = DBAPIError("", None, orig=ValueError())

        with mock.patch("sqlalchemy_hana.errors.wrap_hdbcli_error") as mocked:
            wrap_dbapi_error(error)

        mocked.assert_not_called()


class TestWrapHdbcliError(TestBase):
    def test_wrap_hdbcli_error_txsavepoint_not_found(self) -> None:
        error = HdbcliError(128, "TxSavepoint not found")
        error.__context__ = HdbcliError(133, "some deadlock")

        with pytest.raises(DeadlockError):
            wrap_hdbcli_error(error)

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
        ],
    )
    def test_wrap_hdbcli_error(
        self,
        errorcode: int,
        errortext: str,
        expected_exception: type[Exception],
    ) -> None:
        error = HdbcliError(errorcode, errortext)

        with pytest.raises(expected_exception):
            wrap_hdbcli_error(error)

    @pytest.mark.parametrize(
        "errorcode,errortext",
        [
            (123, "An error occurred while opening the channel"),
            (-10800, ""),
            (123, "some error"),
        ],
    )
    def test_wrap_hdbcli_error_no_wrap(self, errorcode: int, errortext: str) -> None:
        error = HdbcliError(errorcode, errortext)
        wrap_hdbcli_error(error)
