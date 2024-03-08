"""HANA error handling for humans.

This module contains improved error handling for hdbcli errors.
Basically it takes a py:exc:`hdbcli.dbapi.Error` or :py:exc:`sqlalchemy.exc.DBAPIError` instance
and raises a more specific exception if possible.
"""

from __future__ import annotations

from hdbcli.dbapi import Error as HdbcliError
from sqlalchemy.exc import DBAPIError


class HANAError(Exception):
    """Base class for all sqlalchemy-hana errors."""


class SequenceCacheTimeoutError(HANAError):
    """Exception raised when the sequence cache times out."""


class LockWaitTimeoutError(HANAError):
    """Exception raised when a lock wait times out."""


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


def wrap_dbapi_error(error: DBAPIError) -> None:
    """Takes a :py:exc:`sqlalchemy.exc.DBAPIError` and raises a more specific exception if possible.

    For that the :py:data:`sqlalchemy.exc.DBAPIError.orig` attribute is checked for a
    :py:exc:`hdbcli.dbapi.Error`.
    If found, :py:func:`wrap_hdbcli_error` is called with it.
    Else ``None`` is returned.

    Args:
        error: The error to be wrapped

    Returns:
        None
    """
    if isinstance(error.orig, HdbcliError):
        wrap_hdbcli_error(error.orig)


def convert_dbapi_error(error: DBAPIError) -> DBAPIError | HANAError:
    """Takes a :py:exc:`sqlalchemy.exc.DBAPIError` and converts it to a more specific exception.

    Similar to :py:func:`~wrap_dbapi_error`, but instead of throwing the error, it returns it as
    an object.
    """
    try:
        wrap_dbapi_error(error)
    except HANAError as thrown:
        return thrown
    return error


def wrap_hdbcli_error(error: HdbcliError) -> None:
    """Wraps the given :py:exc:`hdbcli.dbapi.Error` and raises specific exception if possible.

    For this, the error code and error text are checked.
    If a specific exception is raised, the original exception is set as the new exception's cause.

    In addition, an edge case is handled where SQLAlchemy creates a savepoint and the same
    transaction later fails leading to an automatic rollback by HANA.
    However, SQLAlchemy still tries to roll back the savepoint, which fails because the savepoint
    is no longer valid.
    In this case, the cause of the exception is used for further processing.

    Args:
        error: The error to be wrapped

    Returns:
        None
    """
    # extract hidden inner exceptions
    # TxSavepoint not found should normally only happen if a transaction was rolled back by HANA,
    # but SQLAlchemy also tries to perform a savepoint rollback, which fails due to the transaction
    # rollback. In this case, we need to check the inner exception (__context__)
    if (
        error.__context__
        and isinstance(error.__context__, HdbcliError)
        and error.errorcode == 128
        and "TxSavepoint not found" in error.errortext
    ):
        error = error.__context__

    if error.errorcode in [-10807, -10709]:  # sqldbc error codes for connection errors
        raise ClientConnectionError from error
    if error.errorcode == 613:
        raise StatementTimeoutError from error
    if (
        error.errorcode == 139
        and "current operation cancelled by request and transaction rolled back"
        in error.errortext
    ):
        raise TransactionCancelledError from error
    if "Lock timeout occurs while waiting sequence cache lock" in str(error.errortext):
        raise SequenceCacheTimeoutError from error
    if error.errorcode == 131:
        raise LockWaitTimeoutError from error
    if error.errorcode == 146:
        raise LockAcquisitionError from error
    if error.errorcode == 133:
        raise DeadlockError from error
    if (
        "OutOfMemory exception" in error.errortext
        or "cannot allocate enough memory" in error.errortext
        or "Allocation failed" in error.errortext
        or error.errorcode == 4
    ):
        raise DatabaseOutOfMemoryError from error
    if (
        error.errorcode == 129
        and "max number of SqlExecutor threads are exceeded" in error.errortext
    ):
        raise DatabaseOverloadedError from error
    if (
        # ERR_SQL_CONNECT_NOT_ALLOWED: user not allowed to connect from client
        error.errorcode == 663
        # GBA503: geo blocking service responded with a 503
        and "Error GBA503: Service is unavailable" in error.errortext
    ):
        raise DatabaseConnectNotPossibleError from error
    if (
        # 129 -> ERR_TX_ROLLBACK: transaction rolled back by an internal error
        error.errorcode in [129, 145]
        or "An error occurred while opening the channel" in error.errortext
        or "Exception in executor plan" in error.errortext
        or "DTX commit(first phase commit) failed" in error.errortext
        or "An error occurred while reading from the channel" in error.errortext
    ):
        raise StatementExecutionError from error
    if error.errorcode == 397:
        raise InvalidObjectNameError from error


__all__ = (
    "wrap_dbapi_error",
    "wrap_hdbcli_error",
    "HANAError",
    "SequenceCacheTimeoutError",
    "LockWaitTimeoutError",
    "LockAcquisitionError",
    "DatabaseConnectNotPossibleError",
    "ClientConnectionError",
    "DatabaseOutOfMemoryError",
    "DeadlockError",
    "DatabaseOverloadedError",
    "StatementExecutionError",
    "InvalidObjectNameError",
    "InternalQueryExecutionError",
    "convert_dbapi_error",
)
