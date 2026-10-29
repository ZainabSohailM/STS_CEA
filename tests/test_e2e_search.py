from __future__ import annotations

import pytest
from playwright.sync_api import expect

from helpers import load_products, seed_marketplace_access, stub_products

pytestmark = [pytest.mark.functional, pytest.mark.crossbrowser]

PRODUCTS = load_products()
PRODUCT_CARD = ".portfolio-container .portfolio-item"
FILTER_INPUT = "#portfolio-query-filter"


def _open(page, base_url):
    seed_marketplace_access(page)
    stub_products(page, PRODUCTS)
    page.goto(f"{base_url}/marketplace", wait_until="domcontentloaded")
    expect(page.locator("#marketplace")).to_be_visible(timeout=60000)
    expect(page.locator(PRODUCT_CARD).first).to_be_visible(timeout=60000)


# --------------------------------------------------------------------------- #
# FLT-01 (positive) — filtering by a product name narrows the grid to matches.
# --------------------------------------------------------------------------- #
def test_flt01_filter_by_name(bc_page, base_url, shot):
    _open(bc_page, base_url)
    total = bc_page.locator(PRODUCT_CARD).count()
    assert total > 1

    bc_page.fill(FILTER_INPUT, "Amethyst")
    expect(bc_page.get_by_role("heading", name="Amethyst", exact=True)).to_be_visible()
    expect(bc_page.get_by_role("heading", name="Ruby", exact=True)).to_have_count(0)
    assert bc_page.locator(PRODUCT_CARD).count() < total
    shot("filter_match")


# --------------------------------------------------------------------------- #
# FLT-02 (positive) — clearing the filter restores the full catalogue.
# --------------------------------------------------------------------------- #
def test_flt02_clear_restores_all(bc_page, base_url):
    _open(bc_page, base_url)
    total = bc_page.locator(PRODUCT_CARD).count()

    bc_page.fill(FILTER_INPUT, "Amethyst")
    assert bc_page.locator(PRODUCT_CARD).count() < total

    bc_page.fill(FILTER_INPUT, "")
    expect(bc_page.locator(PRODUCT_CARD)).to_have_count(total)


# --------------------------------------------------------------------------- #
# FLT-03 (negative) — a no-match term yields an empty result set, no crash.
# --------------------------------------------------------------------------- #
def test_flt03_no_match_empty(bc_page, base_url, shot):
    _open(bc_page, base_url)
    bc_page.fill(FILTER_INPUT, "zzzz_no_such_gem_zzzz")
    expect(bc_page.locator(PRODUCT_CARD)).to_have_count(0)
    # The filter input and section remain usable.
    expect(bc_page.locator(FILTER_INPUT)).to_be_visible()
    shot("filter_no_match")
