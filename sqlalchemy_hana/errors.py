"""HANA error handling for humans.

This module contains improved error handling for hdbcli errors.
Basically it takes a :py:exc:`sqlalchemy.exc.DBAPIError` instance and returns a more specific
exception if possible.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from hdbcli.dbapi import Error as HdbcliError
from sqlalchemy.exc import DBAPIError

if TYPE_CHECKING:
    from typing_extensions import Self


class HANAError(DBAPIError):
    """Base class for all sqlalchemy-hana errors."""

    @classmethod
    def from_dbapi_error(cls, error: DBAPIError) -> Self:
        """Create a new exception instance based on the given dbapi error."""
        return cls(
            statement=error.statement,
            params=error.params,
            orig=cast(BaseException, error.orig),
            hide_parameters=error.hide_parameters,
            code=error.code,
            ismulti=error.ismulti,
        )


class SequenceCacheTimeoutError(HANAError):
    """Exception raised when the sequence cache times out."""


class WriteInReadOnlyReplicationError(HANAError):
    """Exception raised when a write statement is executed in a read only replication."""


class LockWaitTimeoutError(HANAError):
    """Exception raised when a lock wait times out."""


class SequenceLockTimeoutError(LockWaitTimeoutError):
    """Exception raised when a sequence lock wait times out."""


class LockAcquisitionError(HANAError):
    """Exception raised when a lock acquisition fails."""


class DatabaseConnectNotPossibleError(HANAError):
    """Exception raised when the database is unavailable."""


class ClientConnectionError(DatabaseConnectNotPossibleError):
    """Exception raised when a client connection to the database cannot be established."""


class DatabaseOutOfMemoryError(HANAError):
    """Exception raised when the database runs out of memory."""


class DeadlockError(HANAError):
    """Exception raised when a deadlock occurs."""


class DatabaseOverloadedError(HANAError):
    """Exception raised when the database is overloaded."""


class StatementExecutionError(HANAError):
    """Exception raised when there is an error executing a statement in HANA."""


class StatementTimeoutError(HANAError):
    """Exception raised when a statement execution times out."""


class TransactionCancelledError(HANAError):
    """Error raised when a transaction is cancelled."""


class InvalidObjectNameError(HANAError):
    """Error when an invalid object name is referenced."""


def convert_dbapi_error(dbapi_error: DBAPIError) -> DBAPIError:
    """Takes a :py:exc:`sqlalchemy.exc.DBAPIError` and returns a more specific error if possible.

    For that the :py:data:`sqlalchemy.exc.DBAPIError.orig` attribute is checked for a
    :py:exc:`hdbcli.dbapi.Error`.
    If it does not contain a hdbcli error, the original exception is returned.

    Else the error code and error text are further checked.
    """
    error = dbapi_error.orig
    if not isinstance(error, HdbcliError):
        return dbapi_error

    if error.errorcode in [-10807, -10709]:  # sqldbc error codes for connection errors
        return ClientConnectionError.from_dbapi_error(dbapi_error)
    if error.errorcode == 613:
        return StatementTimeoutError.from_dbapi_error(dbapi_error)
    if (
        error.errorcode == 139
        and "current operation cancelled by request and transaction rolled back"
        in error.errortext
    ):
        return TransactionCancelledError.from_dbapi_error(dbapi_error)
    if "Lock timeout occurs while waiting sequence cache lock" in str(error.errortext):
        return SequenceCacheTimeoutError.from_dbapi_error(dbapi_error)
    if (
        error.errorcode == 131
        and "Lock timeout occurs while waiting sequence lock" in error.errortext
    ):
        return SequenceLockTimeoutError.from_dbapi_error(dbapi_error)
    if error.errorcode == 131:
        return LockWaitTimeoutError.from_dbapi_error(dbapi_error)
    if error.errorcode == 146:
        return LockAcquisitionError.from_dbapi_error(dbapi_error)
    if error.errorcode == 133:
        return DeadlockError.from_dbapi_error(dbapi_error)
    if (
        "OutOfMemory exception" in error.errortext
        or "cannot allocate enough memory" in error.errortext
        or "Allocation failed" in error.errortext
        or error.errorcode == 4
    ):
        return DatabaseOutOfMemoryError.from_dbapi_error(dbapi_error)
    if (
        error.errorcode == 129
        and "max number of SqlExecutor threads are exceeded" in error.errortext
    ):
        return DatabaseOverloadedError.from_dbapi_error(dbapi_error)
    if (
        (  # ERR_SQL_CONNECT_NOT_ALLOWED: user not allowed to connect from client
            error.errorcode == 663
            # GBA503: geo blocking service responded with a 503
            and "Error GBA503: Service is unavailable" in error.errortext
        )
        or error.errortext
        in [
            "HANA Cloud region is in maintenance window",
            "HANA Database instance upgrade in progress",
        ]
        # ERR_URS_INSTANCE_NOT_AVAILABLE: HANA Database service is not available
        or error.errorcode == 1888
    ):
        return DatabaseConnectNotPossibleError.from_dbapi_error(dbapi_error)
    if (
        # 129 -> ERR_TX_ROLLBACK: transaction rolled back by an internal error
        error.errorcode in [129, 145]
        or "An error occurred while opening the channel" in error.errortext
        or "Exception in executor plan" in error.errortext
        or "DTX commit(first phase commit) failed" in error.errortext
        or "An error occurred while reading from the channel" in error.errortext
        or "temp index not exists" in error.errortext
    ):
        return StatementExecutionError.from_dbapi_error(dbapi_error)
    if error.errorcode == 397:
        return InvalidObjectNameError.from_dbapi_error(dbapi_error)
    if error.errortext.startswith(
        "feature not supported: writable statement not allowed in read-enabled replication"
    ):
        return WriteInReadOnlyReplicationError.from_dbapi_error(dbapi_error)
    return dbapi_error


__all__ = (
    "ClientConnectionError",
    "DatabaseConnectNotPossibleError",
    "DatabaseOutOfMemoryError",
    "DatabaseOverloadedError",
    "DeadlockError",
    "HANAError",
    "InvalidObjectNameError",
    "LockAcquisitionError",
    "LockWaitTimeoutError",
    "SequenceCacheTimeoutError",
    "SequenceLockTimeoutError",
    "StatementExecutionError",
    "WriteInReadOnlyReplicationError",
    "convert_dbapi_error",
)
