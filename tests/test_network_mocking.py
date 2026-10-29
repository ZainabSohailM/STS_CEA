from __future__ import annotations

import json
import re

import pytest
from playwright.sync_api import expect

from helpers import seed_marketplace_access

pytestmark = [pytest.mark.network, pytest.mark.crossbrowser]

CATALOGUE_RE = re.compile(r"/api/products\?")
PRODUCT_CARD = ".portfolio-container .portfolio-item"


# NET-01 — empty data response.
def test_net01_empty_data_response(bc_page, base_url, shot):
    hits = {"n": 0}

    def handler(route):
        hits["n"] += 1
        route.fulfill(status=200, content_type="application/json", body="[]")

    seed_marketplace_access(bc_page)
    bc_page.route(CATALOGUE_RE, handler)
    bc_page.goto(f"{base_url}/marketplace", wait_until="domcontentloaded")

    expect(bc_page.locator("#marketplace")).to_be_visible(timeout=60000)
    expect(bc_page.locator(PRODUCT_CARD)).to_have_count(0)        # empty grid
    expect(bc_page.locator("#portfolio-query-filter")).to_be_visible()  # still usable
    assert hits["n"] >= 1, "the product request was not intercepted"
    shot("net01_empty_state")


# NET-02 — server error response (reveals a real bug).
def test_net02_server_error_response(bc_page, base_url, shot):
    hits = {"n": 0}

    def handler(route):
        hits["n"] += 1
        route.fulfill(status=500, content_type="application/json",
                      body=json.dumps({"error": "Internal Server Error", "statusCode": 500}))

    seed_marketplace_access(bc_page)
    bc_page.route(CATALOGUE_RE, handler)

    errors = []
    bc_page.on("pageerror", lambda e: errors.append(str(e)))
    bc_page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

    bc_page.goto(f"{base_url}/marketplace", wait_until="domcontentloaded")
    bc_page.wait_for_timeout(3000)

    assert hits["n"] >= 1, "the product request was not intercepted"
    assert bc_page.locator(PRODUCT_CARD).count() == 0
    shot("net02_error_state")
    # The page does not handle the error gracefully — it throws a TypeError
    # because the error body is not a list and the code runs .map() on it.
    assert any("map is not a function" in e for e in errors), (
        f"expected the 500 to surface the unhandled-error bug; errors: {errors}"
    )
