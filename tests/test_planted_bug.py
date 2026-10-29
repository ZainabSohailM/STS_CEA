from __future__ import annotations

import pytest
import requests

from helpers import BASE_URL, PRODUCTS_LATEST

pytestmark = [pytest.mark.planted_bug]


def test_planted_bug_security_header():
    resp = requests.get(f"{BASE_URL}{PRODUCTS_LATEST}", timeout=20)
    value = resp.headers.get("X-Content-Type-Options", "<missing>")
    assert value.lower() == "nosniff", (
        f"X-Content-Type-Options must be 'nosniff' but the site returned {value!r} "
        f"(this failure is intentional — it proves the test catches the bug)"
    )
