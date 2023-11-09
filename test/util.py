"""Utility for tests."""

from __future__ import annotations

import random
import string


def random_string(length: int) -> str:
    """Create a random string with the given length."""
    return "".join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length
        )
    )
