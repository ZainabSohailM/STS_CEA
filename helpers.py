from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCREENSHOTS_DIR = ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# --- Configuration ----------- #
BASE_URL = os.environ.get("BASE_URL", "https://brokencrystals.com").rstrip("/")
LOCAL_API_URL = os.environ.get("LOCAL_API_URL", "http://127.0.0.1:5099").rstrip("/")
ACTION_TIMEOUT = int(os.environ.get("ACTION_TIMEOUT", "45000"))   # ms
NAV_TIMEOUT = int(os.environ.get("NAV_TIMEOUT", "90000"))         # ms

PRODUCTS_LATEST = "/api/products/latest"

# --- Real product data captured from the public API  --- #
PRODUCTS = [
    {"id": 1, "name": "Amethyst", "category": "Healing", "description": "a violet variety of quartz"},
    {"id": 2, "name": "Ruby", "category": "Gemstones", "description": "an intense heart crystal"},
    {"id": 3, "name": "Opal", "category": "Healing", "description": "the precious stone"},
    {"id": 4, "name": "Sapphire", "category": "Jewellery", "description": "a blue gem"},
    {"id": 5, "name": "Amber", "category": "Healing", "description": "fossilized tree resin"},
    {"id": 6, "name": "Emerald", "category": "Jewellery", "description": "symbol of fertility and life"},
    {"id": 7, "name": "Shattuckite", "category": "Jewellery", "description": "mistery"},
    {"id": 8, "name": "Bismuth", "category": "Gemstones", "description": "rainbow"},
    {"id": 9, "name": "Labradorite", "category": "Gemstones", "description": "rainbow"},
    {"id": 10, "name": "Axinite", "category": "Gemstones", "description": "brown"},
    {"id": 11, "name": "Pietersite", "category": "Gemstones", "description": "blue"},
]
for _p in PRODUCTS:
    _p["photoUrl"] = f"/api/file?path=config/products/crystals/{_p['name'].lower()}.jpg&type=image/jpg"


def load_products():
    return [dict(p) for p in PRODUCTS]


# --- Marketplace helpers ---------------------------------------------------- #
PRODUCTS_DATE_RANGE_RE = re.compile(r"/api/products\?")
SEED_EMAIL_SCRIPT = "try { localStorage.setItem('email', 'cea-test@example.com'); } catch (e) {}"


def seed_marketplace_access(page):
    page.add_init_script(SEED_EMAIL_SCRIPT)


def stub_products(page, products, status: int = 200):
    import json

    def handler(route):
        if status == 200:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(products))
        else:
            route.fulfill(status=status, content_type="application/json",
                          body=json.dumps({"error": "stubbed error", "statusCode": status}))

    page.route(PRODUCTS_DATE_RANGE_RE, handler)


# --- CRUD test data (for the local test API) -------------------------------- #
def sample_crystal(suffix: str) -> dict:
    return {
        "name": f"Test Crystal {suffix}",
        "category": "Healing",
        "description": "Automated CRUD test record — safe to delete.",
        "price": 42.5,
    }
