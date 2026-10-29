from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.functional, pytest.mark.crossbrowser]


# --------------------------------------------------------------------------- #
# NAV-01 (positive) — landing page loads and shows the brand/hero.
# --------------------------------------------------------------------------- #
def test_nav01_landing_loads(bc_page, base_url, shot):
    bc_page.goto(base_url, wait_until="domcontentloaded")
    expect(bc_page).to_have_title(re.compile("Broken Crystals", re.I))
    hero = bc_page.get_by_role("heading", name="Your Vulnerable Crystal Marketplace")
    expect(hero).to_be_visible()
    expect(bc_page.get_by_role("heading",
           name="Find the most beautiful stones in one place!")).to_be_visible()
    shot("landing")


# --------------------------------------------------------------------------- #
# NAV-02 (positive) — the access-control guard redirects an anonymous user from
# the Marketplace link to the login page (AppRoutes.tsx guards /marketplace).
# --------------------------------------------------------------------------- #
def test_nav02_marketplace_requires_login(bc_page, base_url, shot):
    bc_page.goto(base_url, wait_until="domcontentloaded")
    marketplace_link = bc_page.get_by_role("link", name="Marketplace").first
    expect(marketplace_link).to_be_visible()
    marketplace_link.click()
    expect(bc_page).to_have_url(re.compile(r"/userlogin"), timeout=90000)
    expect(bc_page.get_by_role("button", name=re.compile("sign in", re.I))).to_be_visible()
    shot("marketplace_requires_login")


# --------------------------------------------------------------------------- #
# NAV-03 (negative) — an unknown route renders the 404 page, not the hero.
# --------------------------------------------------------------------------- #
def test_nav03_unknown_route_shows_404(bc_page, base_url, shot):
    bc_page.goto(f"{base_url}/this-route-does-not-exist-xyz", wait_until="domcontentloaded")
    expect(bc_page.get_by_role("heading", name=re.compile(r"404.*Page Not Found", re.I))).to_be_visible()
    expect(bc_page.get_by_role("heading",
           name="Your Vulnerable Crystal Marketplace")).to_have_count(0)
    shot("not_found")
