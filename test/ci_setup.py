"""Script to setup/teardown a test session."""

from __future__ import annotations

import random
import string
import sys
from contextlib import closing
from urllib.parse import urlsplit

from hdbcli import dbapi


def random_string(length: int) -> str:
    """Create a random string with the given length."""
    return "".join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length
        )
    )


def setup(dburi: str) -> str:
    url = urlsplit(dburi)
    user = f"PYTEST_{random_string(10)}"
    # always fulfill the password policy
    password = random_string(15) + "A1a"

    with (
        closing(
            dbapi.connect(url.hostname, url.port, url.username, url.password)
        ) as connection,
        closing(connection.cursor()) as cursor,
    ):
        cursor.execute(
            f'CREATE USER {user} PASSWORD "{password}" NO FORCE_FIRST_PASSWORD_CHANGE'
        )
        cursor.execute(f"GRANT CREATE SCHEMA TO {user}")

    return f"hana://{user}:{password}@{url.hostname}:{url.port}"


def teardown(dburi: str, test_dburi: str) -> None:
    url = urlsplit(dburi)
    test_user = urlsplit(test_dburi).username

    with (
        closing(
            dbapi.connect(url.hostname, url.port, url.username, url.password)
        ) as connection,
        closing(connection.cursor()) as cursor,
    ):
        cursor.execute(f"DROP USER {test_user} CASCADE")


if __name__ == "__main__":
    if sys.argv[1] == "setup":
        print(setup(sys.argv[2]))
    elif sys.argv[1] == "teardown":
        teardown(sys.argv[2], sys.argv[3])
    else:
        raise ValueError(f"Unknown mode {sys.argv[1]}")
