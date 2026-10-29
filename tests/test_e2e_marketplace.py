from __future__ import annotations

import pytest
from playwright.sync_api import expect

from helpers import load_products, seed_marketplace_access, stub_products

pytestmark = [pytest.mark.functional, pytest.mark.crossbrowser]

PRODUCTS = load_products()
PRODUCT_CARD = ".portfolio-container .portfolio-item"


def _open_marketplace(page, base_url, products=PRODUCTS, status=200):
    seed_marketplace_access(page)
    stub_products(page, products, status=status)
    page.goto(f"{base_url}/marketplace", wait_until="domcontentloaded")
    expect(page.locator("#marketplace")).to_be_visible(timeout=60000)


# --------------------------------------------------------------------------- #
# MKT-01 (positive) — products load and render as cards.
# --------------------------------------------------------------------------- #
def test_mkt01_products_render(bc_page, base_url, shot):
    _open_marketplace(bc_page, base_url)
    cards = bc_page.locator(PRODUCT_CARD)
    expect(cards.first).to_be_visible(timeout=60000)
    assert cards.count() == len(PRODUCTS), (
        f"expected {len(PRODUCTS)} product cards, saw {cards.count()}"
    )
    expect(bc_page.get_by_role("heading", name="Amethyst", exact=True)).to_be_visible()
    shot("catalogue")


# --------------------------------------------------------------------------- #
# MKT-02 (positive) — each product card carries an image with a descriptive alt.
# --------------------------------------------------------------------------- #
def test_mkt02_product_images_and_filters(bc_page, base_url):
    _open_marketplace(bc_page, base_url)
    # ProductView sets alt = "Image of {name}".
    images = bc_page.get_by_role("img", name="Image of Amethyst")
    expect(images.first).to_be_visible()
    filters = bc_page.locator("#portfolio-flters li")
    assert filters.count() >= 2, "expected at least an 'All' filter plus categories"


# --------------------------------------------------------------------------- #
# MKT-03 (negative/boundary) — an empty catalogue response renders a safe empty
# state (zero cards) without crashing the page (unavailable-resource boundary).
# --------------------------------------------------------------------------- #
def test_mkt03_empty_catalogue_safe(bc_page, base_url, shot):
    _open_marketplace(bc_page, base_url, products=[])
    cards = bc_page.locator(PRODUCT_CARD)
    assert cards.count() == 0, "an empty catalogue must render zero product cards"
    expect(bc_page.locator("#portfolio-query-filter")).to_be_visible()
    shot("empty_catalogue_boundary")
